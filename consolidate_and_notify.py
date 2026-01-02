#!/usr/bin/env python3
"""
Consolidate results from multiple environment scans and send a single Slack notification
"""

import json
import os
import sys
import argparse
import requests
from datetime import datetime
from pathlib import Path


def load_results_from_json_files(json_dir):
    """Load all JSON result files from a directory"""
    all_results = {}

    json_files = list(Path(json_dir).glob('**/*.json'))

    if not json_files:
        print(f"No JSON files found in {json_dir}")
        return all_results

    for json_file in json_files:
        print(f"Loading results from {json_file}")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                all_results.update(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")

    return all_results


def send_consolidated_slack_notification(webhook_url, all_results):
    """Send formatted Slack notification with consolidated results from all environments"""

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

    # Add footer
    github_run_url = os.environ.get('GITHUB_RUN_URL')
    footer_text = "💾 Detailed reports available"
    if github_run_url:
        footer_text += f" | <{github_run_url}|View in GitHub Actions>"

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": footer_text
            }
        ]
    })

    payload = {
        "blocks": blocks
    }

    response = requests.post(webhook_url, json=payload)

    if response.status_code == 200:
        print("\n✓ Consolidated Slack notification sent successfully")
    else:
        print(f"\n✗ Failed to send Slack notification: {response.status_code} - {response.text}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Consolidate scan results and send Slack notification')
    parser.add_argument('--json-dir', required=True, help='Directory containing JSON result files')
    parser.add_argument('--slack-webhook', required=True, help='Slack webhook URL')

    args = parser.parse_args()

    print("="*80)
    print("Consolidating AWS Resource Monitor Results")
    print("="*80)

    # Load all results
    all_results = load_results_from_json_files(args.json_dir)

    if not all_results:
        print("\n✗ No results found to consolidate")
        sys.exit(1)

    print(f"\nFound results for environments: {', '.join(all_results.keys())}")

    # Send consolidated Slack notification
    send_consolidated_slack_notification(args.slack_webhook, all_results)

    print("\n" + "="*80)
    print("CONSOLIDATION COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
