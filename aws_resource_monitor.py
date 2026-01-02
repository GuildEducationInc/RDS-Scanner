#!/usr/bin/env python3
"""
AWS Resource Monitor
Scans AWS environments for resource usage and limits:
- Lambda storage and unused functions
- IAM role limits
- Underused RDS instances
- Old CloudWatch log groups

Sends Slack notifications and uploads reports to Google Drive.
"""

import boto3
import csv
import json
import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import argparse
import requests
from io import StringIO


class AWSResourceMonitor:
    def __init__(self, profile, environment, region='us-west-2'):
        """Initialize AWS Resource Monitor."""
        self.environment = environment
        self.profile = profile
        self.region = region

        # Use default credentials if profile is None or empty string
        if profile and profile.strip():
            session = boto3.Session(profile_name=profile, region_name=region)
        else:
            session = boto3.Session(region_name=region)
        self.lambda_client = session.client('lambda', region_name=region)
        self.cloudwatch = session.client('cloudwatch', region_name=region)
        self.rds_client = session.client('rds', region_name=region)
        self.iam_client = session.client('iam')
        self.logs_client = session.client('logs', region_name=region)
        self.sts_client = session.client('sts')

        # Get account ID
        self.account_id = self.sts_client.get_caller_identity()['Account']

        print(f"Initialized monitor for {environment} (Account: {self.account_id}, Region: {region})")

    def scan_lambda_storage(self):
        """Scan Lambda functions for storage usage."""
        print(f"\n[{self.environment}] Scanning Lambda functions...")

        functions = []
        paginator = self.lambda_client.get_paginator('list_functions')

        for page in paginator.paginate():
            functions.extend(page['Functions'])

        print(f"  Found {len(functions)} Lambda functions")

        total_storage = 0
        unused_count = 0
        version_bloat_count = 0

        for i, function in enumerate(functions, 1):
            if i % 100 == 0:
                print(f"  Processed {i}/{len(functions)} functions...")

            function_name = function['FunctionName']

            # Get versions
            versions = []
            try:
                version_paginator = self.lambda_client.get_paginator('list_versions_by_function')
                for page in version_paginator.paginate(FunctionName=function_name):
                    versions.extend(page['Versions'])
            except Exception as e:
                print(f"  Error getting versions for {function_name}: {e}")

            # Calculate storage
            version_count = len(versions)
            storage_bytes = sum(v.get('CodeSize', 0) for v in versions)
            total_storage += storage_bytes

            # Get invocation count
            invocations_30d = self._get_invocation_count(function_name, days=30)

            # Categorize
            if invocations_30d == 0:
                unused_count += 1
            if version_count > 10:
                version_bloat_count += 1

        total_storage_gb = total_storage / (1024 * 1024 * 1024)
        storage_limit_gb = 300
        storage_percent = (total_storage_gb / storage_limit_gb) * 100

        return {
            'total_functions': len(functions),
            'total_storage_gb': round(total_storage_gb, 2),
            'storage_limit_gb': storage_limit_gb,
            'storage_percent': round(storage_percent, 1),
            'unused_count': unused_count,
            'version_bloat_count': version_bloat_count
        }

    def _get_invocation_count(self, function_name, days=30):
        """Get invocation count for last N days."""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=days)

            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400 * days,
                Statistics=['Sum']
            )

            if response['Datapoints']:
                return int(response['Datapoints'][0]['Sum'])
            return 0
        except:
            return 0

    def scan_iam_roles(self):
        """Scan IAM roles and check limits."""
        print(f"\n[{self.environment}] Scanning IAM roles...")

        roles = []
        paginator = self.iam_client.get_paginator('list_roles')

        for page in paginator.paginate():
            roles.extend(page['Roles'])

        # Get IAM account summary for limits
        try:
            summary = self.iam_client.get_account_summary()
            roles_quota = summary['SummaryMap'].get('RolesQuota', 1000)
            roles_count = summary['SummaryMap'].get('Roles', len(roles))
        except:
            roles_quota = 1000
            roles_count = len(roles)

        roles_percent = (roles_count / roles_quota) * 100

        print(f"  Found {roles_count} IAM roles (Limit: {roles_quota})")

        return {
            'total_roles': roles_count,
            'roles_quota': roles_quota,
            'roles_percent': round(roles_percent, 1)
        }

    def scan_rds_instances(self):
        """Scan RDS instances for underutilization."""
        print(f"\n[{self.environment}] Scanning RDS instances...")

        instances = []
        paginator = self.rds_client.get_paginator('describe_db_instances')

        for page in paginator.paginate():
            instances.extend(page['DBInstances'])

        print(f"  Found {len(instances)} RDS instances")

        underused_count = 0
        total_underused = []

        for instance in instances:
            db_id = instance['DBInstanceIdentifier']
            status = instance['DBInstanceStatus']

            if status != 'available':
                continue

            # Get CPU utilization
            try:
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(days=7)

                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_id}],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,
                    Statistics=['Average']
                )

                if response['Datapoints']:
                    avg_cpu = sum(d['Average'] for d in response['Datapoints']) / len(response['Datapoints'])

                    # Consider underused if avg CPU < 10%
                    if avg_cpu < 10:
                        underused_count += 1
                        total_underused.append({
                            'instance': db_id,
                            'avg_cpu': round(avg_cpu, 2),
                            'engine': instance.get('Engine', 'unknown'),
                            'size': instance.get('DBInstanceClass', 'unknown')
                        })
            except Exception as e:
                print(f"  Error checking {db_id}: {e}")

        return {
            'total_instances': len(instances),
            'underused_count': underused_count,
            'underused_details': total_underused
        }

    def scan_cloudwatch_logs(self, days_threshold=90):
        """Scan CloudWatch log groups for old/unused logs."""
        print(f"\n[{self.environment}] Scanning CloudWatch log groups...")

        log_groups = []
        paginator = self.logs_client.get_paginator('describe_log_groups')

        for page in paginator.paginate():
            log_groups.extend(page['logGroups'])

        print(f"  Found {len(log_groups)} log groups")

        old_log_groups = []
        total_storage_bytes = 0
        threshold_time = datetime.now(timezone.utc) - timedelta(days=days_threshold)
        threshold_ms = int(threshold_time.timestamp() * 1000)

        for log_group in log_groups:
            log_group_name = log_group['logGroupName']
            storage_bytes = log_group.get('storedBytes', 0)
            total_storage_bytes += storage_bytes

            # Check last event time
            last_event_time = log_group.get('creationTime', 0)

            # Try to get actual last event time from streams
            try:
                streams_response = self.logs_client.describe_log_streams(
                    logGroupName=log_group_name,
                    orderBy='LastEventTime',
                    descending=True,
                    limit=1
                )
                if streams_response['logStreams']:
                    last_event_time = streams_response['logStreams'][0].get('lastEventTimestamp', last_event_time)
            except:
                pass

            if last_event_time < threshold_ms:
                old_log_groups.append({
                    'name': log_group_name,
                    'storage_mb': round(storage_bytes / (1024 * 1024), 2),
                    'last_event_days': round((datetime.now(timezone.utc).timestamp() * 1000 - last_event_time) / (1000 * 86400))
                })

        return {
            'total_log_groups': len(log_groups),
            'old_log_groups_count': len(old_log_groups),
            'total_storage_gb': round(total_storage_bytes / (1024 * 1024 * 1024), 2),
            'old_log_groups': old_log_groups[:20]  # Top 20 old log groups
        }

def generate_csv_report(all_results):
    """Generate CSV report for all environments."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'aws_resource_report_{timestamp}.csv'

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(['AWS Resource Usage Report'])
        writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])

        for env, results in all_results.items():
            writer.writerow([f'=== {env.upper()} ENVIRONMENT ==='])
            writer.writerow([])

            # Lambda section
            writer.writerow(['Lambda Storage'])
            writer.writerow(['Total Functions', results['lambda']['total_functions']])
            writer.writerow(['Storage Used (GB)', results['lambda']['total_storage_gb']])
            writer.writerow(['Storage Limit (GB)', results['lambda']['storage_limit_gb']])
            writer.writerow(['Storage Usage %', results['lambda']['storage_percent']])
            writer.writerow(['Unused Functions', results['lambda']['unused_count']])
            writer.writerow(['Functions with Version Bloat (>10 versions)', results['lambda']['version_bloat_count']])
            writer.writerow([])

            # IAM section
            writer.writerow(['IAM Roles'])
            writer.writerow(['Total Roles', results['iam']['total_roles']])
            writer.writerow(['Roles Quota', results['iam']['roles_quota']])
            writer.writerow(['Usage %', results['iam']['roles_percent']])
            writer.writerow([])

            # RDS section
            writer.writerow(['RDS Instances'])
            writer.writerow(['Total Instances', results['rds']['total_instances']])
            writer.writerow(['Underused Instances', results['rds']['underused_count']])
            if results['rds']['underused_details']:
                writer.writerow(['Instance Name', 'Avg CPU %', 'Engine', 'Instance Class'])
                for db in results['rds']['underused_details']:
                    writer.writerow([db['instance'], db['avg_cpu'], db['engine'], db['size']])
            writer.writerow([])

            # CloudWatch Logs section
            writer.writerow(['CloudWatch Log Groups'])
            writer.writerow(['Total Log Groups', results['logs']['total_log_groups']])
            writer.writerow(['Old Log Groups (>90 days)', results['logs']['old_log_groups_count']])
            writer.writerow(['Total Storage (GB)', results['logs']['total_storage_gb']])
            writer.writerow([])
            writer.writerow([])

    print(f"\n✓ CSV report generated: {filename}")
    return filename


def send_slack_notification(webhook_url, all_results):
    """Send formatted Slack notification."""

    # Build the message
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 Weekly AWS Resources Usage Alert",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Report Date:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        },
        {
            "type": "divider"
        }
    ]

    for env, results in all_results.items():
        env_upper = env.upper()

        # Lambda section
        lambda_emoji = "🔴" if results['lambda']['storage_percent'] > 70 else "🟡" if results['lambda']['storage_percent'] > 50 else "🟢"
        iam_emoji = "🔴" if results['iam']['roles_percent'] > 80 else "🟡" if results['iam']['roles_percent'] > 60 else "🟢"

        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{env_upper} Environment*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"{iam_emoji} *IAM Roles in {env_upper}*\n{results['iam']['total_roles']} / {results['iam']['roles_quota']} ({results['iam']['roles_percent']}%)"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{lambda_emoji} *Lambda Storage in {env_upper}*\n{results['lambda']['total_storage_gb']} / {results['lambda']['storage_limit_gb']} GB ({results['lambda']['storage_percent']}%)"
                    }
                ]
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Bloated Lambdas:* {results['lambda']['version_bloat_count']}\n*Unused Lambdas:* {results['lambda']['unused_count']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Underused RDS:* {results['rds']['underused_count']} / {results['rds']['total_instances']}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Old CloudWatch Logs:* {results['logs']['old_log_groups_count']} log groups (>90 days) | Total: {results['logs']['total_storage_gb']} GB"
                }
            },
            {
                "type": "divider"
            }
        ])

    # Add CSV report info
    csv_report_text = "💾 Detailed CSV report generated"
    github_run_url = os.environ.get('GITHUB_RUN_URL')
    if github_run_url:
        csv_report_text += f" | <{github_run_url}|View artifacts in GitHub Actions>"

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": csv_report_text
            }
        ]
    })

    payload = {
        "blocks": blocks
    }

    response = requests.post(webhook_url, json=payload)

    if response.status_code == 200:
        print("\n✓ Slack notification sent successfully")
    else:
        print(f"\n✗ Failed to send Slack notification: {response.status_code} - {response.text}")


def upload_to_google_drive(filename, credentials_file=None):
    """Upload CSV to Google Drive."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        # Use provided credentials or look for default
        if credentials_file is None:
            credentials_file = os.environ.get('GOOGLE_CREDENTIALS_FILE', 'google-credentials.json')

        if not os.path.exists(credentials_file):
            print(f"\n⚠ Google Drive credentials not found at {credentials_file}")
            print("  Skipping Google Drive upload. To enable:")
            print("  1. Create a service account in Google Cloud Console")
            print("  2. Download credentials JSON")
            print("  3. Set GOOGLE_CREDENTIALS_FILE environment variable or pass --google-credentials")
            return None

        # Authenticate
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )

        service = build('drive', 'v3', credentials=credentials)

        # Upload file
        file_metadata = {
            'name': filename,
            'mimeType': 'text/csv'
        }

        # Check if folder ID is provided
        folder_id = os.environ.get('GOOGLE_DRIVE_FOLDER_ID')
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(filename, mimetype='text/csv')

        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()

        print(f"\n✓ Uploaded to Google Drive: {file.get('webViewLink')}")
        return file.get('id')

    except ImportError:
        print("\n⚠ Google Drive upload requires: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return None
    except Exception as e:
        print(f"\n✗ Failed to upload to Google Drive: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='AWS Resource Monitor - Multi-environment scanner')
    parser.add_argument('--slack-webhook', help='Slack webhook URL')
    parser.add_argument('--skip-slack', action='store_true', help='Skip sending Slack notification')
    parser.add_argument('--google-credentials', help='Path to Google service account credentials JSON')
    parser.add_argument('--dev-profile', default='guild-dev', help='AWS profile for dev environment')
    parser.add_argument('--stage-profile', default='guild-stage', help='AWS profile for staging environment')
    parser.add_argument('--prod-profile', default='guild-prod', help='AWS profile for production environment')
    parser.add_argument('--region', default='us-west-2', help='AWS region (default: us-west-2)')
    parser.add_argument('--environments', default='dev,stage', help='Comma-separated list of environments to scan: dev, stage, prod, or any combination (default: dev,stage)')
    parser.add_argument('--output-json', help='Save results to JSON file for later consolidation')

    args = parser.parse_args()

    print("="*80)
    print("AWS Resource Monitor")
    print("="*80)

    # Parse which environments to scan
    env_list = [e.strip() for e in args.environments.split(',')]

    # Build environment list
    environments = []
    if 'dev' in env_list:
        environments.append(('dev', args.dev_profile))
    if 'stage' in env_list:
        environments.append(('stage', args.stage_profile))
    if 'prod' in env_list:
        environments.append(('prod', args.prod_profile))

    all_results = {}

    for env_name, profile in environments:
        print(f"\n{'='*80}")
        print(f"Scanning {env_name.upper()} environment...")
        print(f"{'='*80}")

        try:
            monitor = AWSResourceMonitor(profile, env_name, args.region)

            results = {
                'lambda': monitor.scan_lambda_storage(),
                'iam': monitor.scan_iam_roles(),
                'rds': monitor.scan_rds_instances(),
                'logs': monitor.scan_cloudwatch_logs()
            }

            all_results[env_name] = results

            print(f"\n{'='*80}")
            print(f"{env_name.upper()} SUMMARY")
            print(f"{'='*80}")
            print(f"Lambda Storage: {results['lambda']['total_storage_gb']}/{results['lambda']['storage_limit_gb']} GB ({results['lambda']['storage_percent']}%)")
            print(f"  - Unused functions: {results['lambda']['unused_count']}")
            print(f"  - Version bloat: {results['lambda']['version_bloat_count']}")
            print(f"IAM Roles: {results['iam']['total_roles']}/{results['iam']['roles_quota']} ({results['iam']['roles_percent']}%)")
            print(f"RDS Instances: {results['rds']['underused_count']} underused / {results['rds']['total_instances']} total")
            print(f"CloudWatch Logs: {results['logs']['old_log_groups_count']} old log groups / {results['logs']['total_log_groups']} total")

        except Exception as e:
            print(f"\n✗ Error scanning {env_name}: {e}")
            import traceback
            traceback.print_exc()

    if not all_results:
        print("\n✗ No results to report")
        return

    # Generate CSV report (doesn't require AWS credentials)
    csv_filename = generate_csv_report(all_results)

    # Save results to JSON if requested
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\n✓ Results saved to JSON: {args.output_json}")

    # Upload to Google Drive
    if args.google_credentials:
        upload_to_google_drive(csv_filename, args.google_credentials)
    else:
        upload_to_google_drive(csv_filename)

    # Send Slack notification (unless skipped)
    if not args.skip_slack:
        if not args.slack_webhook:
            print("\n⚠ Warning: --slack-webhook required when not using --skip-slack")
        else:
            send_slack_notification(args.slack_webhook, all_results)
            print(f"Slack notification sent: {args.slack_webhook[:50]}...")

    print(f"\n{'='*80}")
    print("MONITORING COMPLETE")
    print(f"{'='*80}")
    print(f"CSV Report: {csv_filename}")


if __name__ == "__main__":
    main()
