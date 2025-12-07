# CloudFormation Deployment Guide - RDS Scanner with Slack Integration

## Overview

This CloudFormation template deploys a complete serverless RDS scanning solution that:
- 🔍 Scans RDS databases across multiple regions
- 📅 Runs automatically every **Monday** and **Friday** at 9 AM UTC
- 🔔 Sends formatted reports to **Slack**
- ⏰ **Monday messages include a REMINDER pretext** to review databases
- 💾 Stores detailed reports in S3
- 💰 Estimates potential cost savings

## Architecture

```
EventBridge (Monday/Friday) → Lambda Function → RDS + CloudWatch
                                     ↓
                              S3 Bucket (Reports)
                                     ↓
                              Slack Webhook (Notifications)
```

## Prerequisites

### 1. Slack Webhook Setup

Create a Slack Incoming Webhook:

1. Go to your Slack workspace settings
2. Navigate to **Apps** → **Incoming Webhooks**
3. Click **Add to Slack**
4. Select a channel (e.g., `#cloud-ops` or `#database-alerts`)
5. Copy the Webhook URL (looks like: `https://hooks.slack.com/services/XXX/YYY/ZZZ`)

**Detailed Steps:**
- Visit: https://api.slack.com/messaging/webhooks
- Click "Create your Slack app"
- Choose "From scratch"
- Name your app (e.g., "RDS Scanner")
- Select your workspace
- Go to "Incoming Webhooks" and activate it
- Click "Add New Webhook to Workspace"
- Choose your channel
- Copy the webhook URL

### 2. AWS CLI

Ensure AWS CLI is installed and configured:
```bash
aws --version
aws configure
```

### 3. IAM Permissions

You need permissions to create:
- Lambda functions
- IAM roles and policies
- S3 buckets
- EventBridge rules
- CloudWatch log groups

## Quick Deployment

### Step 1: Download Files

Ensure you have:
- `rds-scanner-cloudformation.yaml`
- `parameters.json`

### Step 2: Update Parameters

Edit `parameters.json` with your values:

```json
[
  {
    "ParameterKey": "SlackWebhookURL",
    "ParameterValue": "https://hooks.slack.com/services/YOUR/ACTUAL/WEBHOOK"
  },
  {
    "ParameterKey": "ScanRegions",
    "ParameterValue": "us-east-1,us-west-2,eu-west-1"
  }
]
```

### Step 3: Deploy Stack

```bash
aws cloudformation create-stack \
  --stack-name rds-scanner \
  --template-body file://rds-scanner-cloudformation.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Step 4: Monitor Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name rds-scanner \
  --query 'Stacks[0].StackStatus'

# Watch events
aws cloudformation describe-stack-events \
  --stack-name rds-scanner \
  --max-items 10
```

Wait for status: `CREATE_COMPLETE` (usually 2-3 minutes)

## Configuration Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| **SlackWebhookURL** | Slack webhook URL for notifications | *Required* | https://hooks.slack.com/services/... |
| **ScanRegions** | Comma-separated AWS regions to scan | us-east-1,us-west-2 | us-east-1,us-west-2,eu-west-1 |
| **ProjectName** | Project name for resource naming | rds-scanner | my-rds-scanner |
| **LambdaTimeout** | Lambda timeout in seconds (300-900) | 900 | 600 |
| **LambdaMemorySize** | Lambda memory in MB | 512 | 1024 |
| **ReportRetentionDays** | S3 report retention period | 90 | 30 |
| **CPUThreshold** | CPU % threshold for underused DBs | 50 | 40 |
| **TransactionThreshold** | Transaction/month threshold | 50 | 100 |

## Schedule Configuration

### Default Schedules
- **Monday**: 9:00 AM UTC with reminder pretext
- **Friday**: 9:00 AM UTC without reminder

### Customize Schedule

To change the schedule, update the `ScheduleExpression` in the template:

```yaml
# Run every Monday at 9 AM UTC
ScheduleExpression: 'cron(0 9 ? * MON *)'

# Run every Friday at 2 PM UTC
ScheduleExpression: 'cron(0 14 ? * FRI *)'

# Run daily at 8 AM UTC
ScheduleExpression: 'cron(0 8 * * ? *)'

# Run on 1st and 15th of month at 10 AM UTC
ScheduleExpression: 'cron(0 10 1,15 * ? *)'
```

**Cron Format**: `cron(Minutes Hours Day Month DayOfWeek Year)`

## Testing the Deployment

### Test Lambda Function Manually

```bash
# Test without Monday reminder
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": false}' \
  response.json

cat response.json

# Test with Monday reminder
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": true}' \
  response.json
```

### Check Slack Message

After running the test, you should see a formatted message in your Slack channel with:
- Total database count
- Unused/Underused/Active breakdown
- Potential cost savings
- Top 5 unused databases
- Top 5 underused databases
- Link to S3 report

**Monday message includes:** ⏰ Reminder pretext at the top

### View Lambda Logs

```bash
aws logs tail /aws/lambda/rds-scanner-function --follow
```

## Slack Message Format

### Friday Message (Normal)
```
🗄️ RDS Database Scan Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Databases: 25
Scan Date: 2024-12-04 09:00 UTC
❌ Unused: 5
⚠️ Underused: 8
✅ Active: 12
💰 Potential Savings: ~$900/month

━━━━━━━━━━━━━━━━━━━━━━━━━━━

Unused Databases (Zero transactions in 6 months):
• `legacy-mysql-db` (mysql) - Owner: john@company.com
• `old-test-db` (postgres) - Owner: N/A
...

Underused Databases (CPU < 50% OR transactions < 50/month):
• `analytics-db` - CPU: 15.23%; Transactions/month: 124 - Owner: analytics@company.com
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Full Report:
s3://rds-scanner-reports-123456789012/rds-scans/rds_scan_20241204_090015.csv
```

### Monday Message (With Reminder)
```
⏰ REMINDER: Weekly RDS Database Scan - Please review unused and underused databases for cost optimization!

━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗄️ RDS Database Scan Results
...
(same format as above)
```

## Viewing Reports

### Access S3 Reports

```bash
# List all reports
aws s3 ls s3://rds-scanner-reports-YOUR-ACCOUNT-ID/rds-scans/

# Download latest report
aws s3 cp s3://rds-scanner-reports-YOUR-ACCOUNT-ID/rds-scans/rds_scan_TIMESTAMP.csv ./
```

### Report Columns

The CSV contains:
- `db_identifier` - Database name
- `engine` - Database engine (postgres, mysql, etc.)
- `instance_class` - Instance type (db.t3.micro, etc.)
- `status` - Database status
- `region` - AWS region
- `category` - Unused/Underused/Active
- `reason` - Explanation for categorization
- `cpu_utilization_6mo` - Average CPU over 6 months
- `transactions_6mo` - Total transactions over 6 months
- `transactions_1mo` - Total transactions last month
- `owner` - Owner tag
- `contact` - Contact tag
- `repo` - Repository tag
- `environment` - Environment tag

## Updating the Stack

### Update Parameters Only

```bash
aws cloudformation update-stack \
  --stack-name rds-scanner \
  --use-previous-template \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### Update Template

```bash
aws cloudformation update-stack \
  --stack-name rds-scanner \
  --template-body file://rds-scanner-cloudformation.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### Update Slack Webhook URL

```bash
aws cloudformation update-stack \
  --stack-name rds-scanner \
  --use-previous-template \
  --parameters \
    ParameterKey=SlackWebhookURL,ParameterValue=https://hooks.slack.com/services/NEW/WEBHOOK/URL \
    ParameterKey=ScanRegions,UsePreviousValue=true \
    ParameterKey=ProjectName,UsePreviousValue=true \
    ParameterKey=LambdaTimeout,UsePreviousValue=true \
    ParameterKey=LambdaMemorySize,UsePreviousValue=true \
    ParameterKey=ReportRetentionDays,UsePreviousValue=true \
    ParameterKey=CPUThreshold,UsePreviousValue=true \
    ParameterKey=TransactionThreshold,UsePreviousValue=true \
  --capabilities CAPABILITY_NAMED_IAM
```

## Monitoring

### CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/rds-scanner-function --since 1h

# Follow logs in real-time
aws logs tail /aws/lambda/rds-scanner-function --follow
```

### Lambda Metrics

```bash
# Get function information
aws lambda get-function --function-name rds-scanner-function

# Get recent invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=rds-scanner-function \
  --start-time 2024-12-01T00:00:00Z \
  --end-time 2024-12-04T23:59:59Z \
  --period 86400 \
  --statistics Sum
```

### EventBridge Rules

```bash
# Check Monday rule
aws events describe-rule --name rds-scanner-monday-schedule

# Check Friday rule
aws events describe-rule --name rds-scanner-friday-schedule

# Disable Monday schedule temporarily
aws events disable-rule --name rds-scanner-monday-schedule

# Re-enable it
aws events enable-rule --name rds-scanner-monday-schedule
```

## Troubleshooting

### Issue: Stack creation fails

**Check validation:**
```bash
aws cloudformation validate-template \
  --template-body file://rds-scanner-cloudformation.yaml
```

**View failure reason:**
```bash
aws cloudformation describe-stack-events \
  --stack-name rds-scanner \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`]'
```

### Issue: Lambda times out

**Solution**: Increase timeout in parameters:
```json
{
  "ParameterKey": "LambdaTimeout",
  "ParameterValue": "900"
}
```

### Issue: Not receiving Slack messages

**Check:**
1. Verify webhook URL is correct
2. Test webhook manually:
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  YOUR_WEBHOOK_URL
```
3. Check Lambda logs for errors
4. Ensure Lambda has internet access (VPC configuration if applicable)

### Issue: No CloudWatch metrics

**Solution**: 
- Ensure Enhanced Monitoring is enabled on RDS instances
- Wait 24-48 hours for metrics to populate
- Check RDS instances are in the scanned regions

### Issue: Missing database tags

**Solution**: Add required tags to your RDS instances:
```bash
aws rds add-tags-to-resource \
  --resource-name arn:aws:rds:us-east-1:123456789012:db:mydb \
  --tags Key=Owner,Value=john@company.com \
         Key=Contact,Value=john@company.com \
         Key=Repo,Value=github.com/company/myrepo
```

## Cost Estimation

### AWS Resources Cost

| Resource | Estimated Cost |
|----------|---------------|
| Lambda (2 invocations/week) | ~$0.50/month |
| S3 Storage | ~$0.10/month |
| CloudWatch Logs | ~$0.50/month |
| CloudWatch API calls | Free tier |
| EventBridge | Free |
| **Total** | **~$1-2/month** |

### Potential Savings

By identifying and removing unused/underused databases:
- Small team: $500-1,000/month
- Medium company: $2,000-5,000/month
- Enterprise: $10,000+/month

**ROI: 500-10,000x** 🎯

## Security Best Practices

1. **Slack Webhook**: Store in AWS Secrets Manager for production:
```bash
aws secretsmanager create-secret \
  --name rds-scanner/slack-webhook \
  --secret-string "https://hooks.slack.com/services/YOUR/WEBHOOK"
```

2. **IAM Least Privilege**: The template follows least privilege principles

3. **S3 Encryption**: Reports bucket uses AES-256 encryption

4. **VPC**: For enhanced security, deploy Lambda in VPC with NAT gateway

5. **Tags**: Add compliance tags to all resources

## Cleanup

### Delete Stack

```bash
# Empty S3 bucket first
aws s3 rm s3://rds-scanner-reports-YOUR-ACCOUNT-ID --recursive

# Delete stack
aws cloudformation delete-stack --stack-name rds-scanner

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name rds-scanner
```

### Verify Deletion

```bash
aws cloudformation describe-stacks --stack-name rds-scanner
# Should return: "Stack with id rds-scanner does not exist"
```

## Advanced Configuration

### Multi-Account Scanning

To scan databases across multiple AWS accounts:

1. Set up cross-account IAM roles
2. Modify Lambda to assume roles
3. See `multi-account-setup.md` for details

### Custom Slack Formatting

Edit the `format_slack_message` function in the CloudFormation template to customize:
- Colors and emojis
- Message structure
- Additional metrics
- Action buttons

### Integration with JIRA/ServiceNow

Add code to create tickets for unused databases automatically.

### Email Notifications

Add SNS topic to send email in addition to Slack.

## Support

### Resources
- CloudFormation documentation: https://docs.aws.amazon.com/cloudformation/
- Lambda documentation: https://docs.aws.amazon.com/lambda/
- EventBridge documentation: https://docs.aws.amazon.com/eventbridge/
- Slack webhooks: https://api.slack.com/messaging/webhooks

### Getting Help
1. Check CloudWatch Logs
2. Review stack events
3. Test components individually
4. Verify IAM permissions

## Next Steps

1. ✅ Deploy the stack
2. ✅ Test manually with `aws lambda invoke`
3. ✅ Verify Slack notifications
4. ✅ Review first report
5. ✅ Tag untagged databases
6. ✅ Take action on unused databases
7. ✅ Monitor weekly reports
8. ✅ Track cost savings

Happy scanning! 🎉
