"""
AWS Lambda Handler for RDS Scanner
Serverless deployment for automated database scanning
"""

import json
import os
import boto3
from datetime import datetime
from rds_scanner import RDSScanner, export_to_csv, export_to_json


def send_sns_notification(topic_arn: str, subject: str, message: str):
    """Send SNS notification with scan results"""
    sns_client = boto3.client('sns')
    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
    except Exception as e:
        print(f"Error sending SNS notification: {e}")


def upload_to_s3(filename: str, bucket: str, key: str):
    """Upload results to S3 bucket"""
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(filename, bucket, key)
        print(f"Uploaded {filename} to s3://{bucket}/{key}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")


def lambda_handler(event, context):
    """
    Lambda handler for RDS scanning
    
    Environment Variables:
    - REGIONS: Comma-separated list of regions (e.g., "us-east-1,us-west-2")
    - S3_BUCKET: S3 bucket for storing results
    - SNS_TOPIC_ARN: SNS topic for notifications (optional)
    - SLACK_WEBHOOK_URL: Slack webhook URL for notifications (optional)
    - SCAN_ENVIRONMENTS: Comma-separated environment names (e.g., "dev,stage,prod")
    """
    
    # Get configuration from environment variables
    regions = os.environ.get('REGIONS', 'us-east-1').split(',')
    s3_bucket = os.environ.get('S3_BUCKET')
    sns_topic = os.environ.get('SNS_TOPIC_ARN')
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    
    # Lambda uses the execution role, so no profile needed
    all_results = []
    
    for region in regions:
        region = region.strip()
        try:
            print(f"Scanning region: {region}")
            scanner = RDSScanner(region=region)
            results = scanner.scan_databases()
            all_results.extend(results)
        except Exception as e:
            print(f"Error scanning region {region}: {e}")
            continue
    
    if not all_results:
        return {
            'statusCode': 200,
            'body': json.dumps('No databases found')
        }
    
    # Generate timestamp for filenames
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    # Export results to temp files (Lambda has /tmp storage)
    csv_filename = f'/tmp/rds_scan_{timestamp}.csv'
    json_filename = f'/tmp/rds_scan_{timestamp}.json'
    
    export_to_csv(all_results, csv_filename)
    export_to_json(all_results, json_filename)
    
    # Upload to S3 if configured
    if s3_bucket:
        upload_to_s3(csv_filename, s3_bucket, f'rds-scans/rds_scan_{timestamp}.csv')
        upload_to_s3(json_filename, s3_bucket, f'rds-scans/rds_scan_{timestamp}.json')
    
    # Generate summary
    unused = [r for r in all_results if r['category'] == 'Unused']
    underused = [r for r in all_results if r['category'] == 'Underused']
    
    summary = f"""
RDS Database Scan Summary
Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

Total Databases: {len(all_results)}
- Unused: {len(unused)}
- Underused: {len(underused)}
- Active: {len(all_results) - len(unused) - len(underused)}

Unused Databases (0 transactions in 6 months):
{chr(10).join([f"  - {db['db_identifier']} ({db['engine']}) - Owner: {db['owner']}" for db in unused[:10]])}
{f"  ... and {len(unused) - 10} more" if len(unused) > 10 else ""}

Underused Databases (CPU < 50% OR transactions < 50/month):
{chr(10).join([f"  - {db['db_identifier']} ({db['engine']}) - {db['reason']} - Owner: {db['owner']}" for db in underused[:10]])}
{f"  ... and {len(underused) - 10} more" if len(underused) > 10 else ""}

Results uploaded to: s3://{s3_bucket}/rds-scans/
"""
    
    # Send SNS notification if configured
    if sns_topic:
        send_sns_notification(
            sns_topic,
            f"RDS Database Scan Results - {len(unused)} Unused, {len(underused)} Underused",
            summary
        )
    
    # Send Slack notification if configured
    if slack_webhook:
        try:
            from slack_notifier import SlackNotifier
            
            # Build S3 URL if bucket is available
            s3_url = None
            if s3_bucket:
                s3_url = f"https://{s3_bucket}.s3.amazonaws.com/rds-scans/rds_scan_{timestamp}.csv"
            
            notifier = SlackNotifier(slack_webhook)
            notifier.send_scan_results(all_results, s3_url)
            print("✓ Slack notification sent successfully")
        except Exception as e:
            print(f"✗ Error sending Slack notification: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'total_databases': len(all_results),
            'unused': len(unused),
            'underused': len(underused),
            'csv_file': f's3://{s3_bucket}/rds-scans/rds_scan_{timestamp}.csv' if s3_bucket else None,
            'json_file': f's3://{s3_bucket}/rds-scans/rds_scan_{timestamp}.json' if s3_bucket else None
        })
    }


# For local testing
if __name__ == '__main__':
    # Set environment variables for testing
    os.environ['REGIONS'] = 'us-east-1'
    os.environ['S3_BUCKET'] = 'my-rds-reports-bucket'
    os.environ['SNS_TOPIC_ARN'] = 'arn:aws:sns:us-east-1:123456789012:rds-alerts'
    os.environ['SLACK_WEBHOOK_URL'] = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    
    # Test the handler
    result = lambda_handler({}, {})
    print(json.dumps(result, indent=2))
