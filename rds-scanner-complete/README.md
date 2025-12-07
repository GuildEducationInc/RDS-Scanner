# AWS RDS Database Scanner

Automated tool to scan AWS RDS instances across multiple environments (dev/stage/prod) and identify:
- **Unused databases**: Zero transactions in the last 6 months
- **Underused databases**: CPU utilization < 50% OR total transactions/month < 50
- Extracts tags: owner, contact, repo, environment

## Features

- 🔍 Scans all RDS instances across multiple AWS accounts/profiles
- 📊 Analyzes CloudWatch metrics (CPU utilization, IOPS, connections)
- 🏷️ Extracts database tags (owner, contact, repo)
- 📈 Generates detailed CSV and JSON reports
- 🌍 Supports multiple regions and AWS profiles
- 📋 Provides summary statistics
- 💬 Slack integration for automated notifications
- 📅 Configurable scheduling (e.g., every Monday)

## Prerequisites

- Python 3.7 or higher
- AWS CLI configured with appropriate credentials
- IAM permissions (see below)

## Installation

1. Clone or download the script files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS profiles for your environments:
```bash
# Configure profiles for different environments
aws configure --profile dev
aws configure --profile stage
aws configure --profile prod
```

## IAM Permissions Required

The AWS user/role running this script needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances",
        "rds:ListTagsForResource"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricStatistics"
      ],
      "Resource": "*"
    }
  ]
}
```

See `iam_policy.json` for the complete policy document.

## Usage

### Basic Usage (Single Profile & Region)

```bash
python rds_scanner.py
```

This scans RDS instances using the default AWS profile in us-east-1.

### Scan Multiple Environments

```bash
python rds_scanner.py --profiles dev stage prod --regions us-east-1 us-west-2
```

### Specify Custom Output File

```bash
python rds_scanner.py --output my_report.csv --json-output my_report.json
```

### Complete Example

```bash
python rds_scanner.py \
  --profiles dev stage prod \
  --regions us-east-1 us-west-2 eu-west-1 \
  --output rds_audit_2024.csv \
  --json-output rds_audit_2024.json
```

### With Slack Notifications

```bash
python rds_scanner.py \
  --profiles prod \
  --regions us-east-1 us-west-2 \
  --slack-webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**For complete Slack setup**: See [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)

## Command Line Arguments

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `--profiles` | AWS profile names to scan | `default` | `--profiles dev stage prod` |
| `--regions` | AWS regions to scan | `us-east-1` | `--regions us-east-1 us-west-2` |
| `--output` | CSV output filename | `rds_scan_results.csv` | `--output report.csv` |
| `--json-output` | JSON output filename | `rds_scan_results.json` | `--json-output report.json` |
| `--slack-webhook` | Slack webhook URL for notifications | None | `--slack-webhook https://hooks.slack.com/...` |
| `--s3-url` | S3 URL for report link in Slack | None | `--s3-url https://bucket.s3.amazonaws.com/report.csv` |

## Output Format

### CSV Report Columns

| Column | Description |
|--------|-------------|
| db_identifier | RDS instance identifier |
| engine | Database engine (postgres, mysql, etc.) |
| instance_class | Instance type (db.t3.micro, etc.) |
| status | Database status (available, stopped, etc.) |
| region | AWS region |
| profile | AWS profile/environment |
| category | Unused, Underused, or Active |
| reason | Explanation for categorization |
| cpu_utilization_6mo | Average CPU over 6 months |
| transactions_6mo | Total transactions over 6 months |
| transactions_1mo | Total transactions in last month |
| owner | Owner tag value |
| contact | Contact tag value |
| repo | Repository tag value |
| environment | Environment tag value |

### JSON Report

The JSON output contains the same information in a structured format, including the full ARN for each database.

## How It Works

### Unused Databases
A database is classified as "Unused" if:
- It has **zero transactions** in the last 6 months
- Transactions are measured by Read IOPS + Write IOPS

### Underused Databases
A database is classified as "Underused" if:
- Average CPU utilization < 50% over the last 6 months **OR**
- Total transactions < 50 per month

### Metrics Used

The scanner uses the following CloudWatch metrics:

- **CPUUtilization**: Average CPU usage over 6 months
- **ReadIOPS**: Read I/O operations per second (proxy for read transactions)
- **WriteIOPS**: Write I/O operations per second (proxy for write transactions)

## Tagging Conventions

The script looks for the following tags (case-insensitive):

- `Owner` or `owner`
- `Contact` or `contact`
- `Repo`, `repo`, or `Repository`
- `Environment` or `environment`

**Tip**: Ensure your databases are properly tagged for accurate reporting.

## Example Output

```
================================================================================
Scanning RDS instances in region: us-east-1, profile: prod
================================================================================

Found 15 database instances

Analyzing: my-postgres-db (postgres)...
Analyzing: legacy-mysql-db (mysql)...
Analyzing: analytics-aurora (aurora-postgresql)...
...

================================================================================
Results exported to: rds_scan_results.csv
================================================================================
Results also exported to: rds_scan_results.json

================================================================================
SUMMARY
================================================================================
Total databases scanned: 15
  - Unused (0 transactions in 6 months): 3
  - Underused (CPU < 50% OR transactions < 50/month): 5
  - Active: 7

Unused databases:
  - legacy-mysql-db (mysql) - Owner: john.doe@company.com
  - old-test-db (postgres) - Owner: N/A
  - staging-backup-db (aurora-mysql) - Owner: team-data@company.com

Underused databases:
  - analytics-db (postgres) - CPU: 15.23%; Transactions/month: 124 - Owner: analytics@company.com
  - reporting-db (mysql) - CPU: 32.45%; Transactions/month: 28 - Owner: reports@company.com
  ...
```

## Scheduling with Cron

To run this automatically, add a cron job:

```bash
# Edit crontab
crontab -e

# Run every Monday at 9 AM
0 9 * * 1 /usr/bin/python3 /path/to/rds_scanner.py --profiles dev stage prod --output /reports/rds_scan_$(date +\%Y\%m\%d).csv
```

## Scheduling with AWS Lambda

For a serverless approach, you can deploy this as a Lambda function:

1. Package the script with dependencies
2. Set up environment variables for profiles/regions
3. Configure CloudWatch Events to trigger weekly
4. Store results in S3

See `lambda_deployment/` directory for Lambda deployment examples.

## Troubleshooting

### Issue: "No credentials found"
**Solution**: Configure AWS CLI or set environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

### Issue: "Access Denied" errors
**Solution**: Ensure your IAM user/role has the required permissions (see IAM Permissions section)

### Issue: No CloudWatch data available
**Solution**: 
- Ensure CloudWatch monitoring is enabled for your RDS instances
- Check that the instances have been running for at least a few days
- Verify the correct region is being scanned

### Issue: Tags showing as "N/A"
**Solution**: 
- Add the required tags to your RDS instances
- Verify tag names match the expected values (Owner, Contact, Repo)
- Check IAM permissions include `rds:ListTagsForResource`

## Cost Considerations

This script makes API calls to:
- RDS (DescribeDBInstances, ListTagsForResource)
- CloudWatch (GetMetricStatistics)

These are typically covered by AWS Free Tier, but for large numbers of databases or frequent scans, review the [AWS pricing page](https://aws.amazon.com/cloudwatch/pricing/).

## Best Practices

1. **Tag your databases**: Ensure all databases have Owner, Contact, and Repo tags
2. **Run regularly**: Schedule weekly or monthly scans to track trends
3. **Review unused databases**: Archive or delete unused databases to save costs
4. **Right-size underused databases**: Consider downgrading instance classes for underused databases
5. **Document exceptions**: Some databases may be legitimately low-usage (backups, DR instances)

## Contributing

Feel free to submit issues or pull requests to improve this tool!

## License

MIT License

## Support

For issues or questions:
- Check the Troubleshooting section
- Review AWS CloudWatch and RDS documentation
- Open an issue in the repository
