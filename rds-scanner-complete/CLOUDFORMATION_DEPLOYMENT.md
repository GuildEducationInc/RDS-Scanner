# CloudFormation Deployment Guide - RDS Scanner with Slack Integration

## 🚀 Quick Deployment

Deploy the entire solution with a single CloudFormation stack that includes:
- Lambda function for RDS scanning
- EventBridge schedules (Monday with reminder + Friday)
- S3 bucket for reports
- Slack integration via webhooks
- IAM roles and permissions

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Slack Workspace** with admin access
3. **AWS CLI** installed and configured

## Step 1: Create Slack Incoming Webhook

### Option A: Using Slack App (Recommended)

1. Go to your Slack workspace: https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Enter:
   - App Name: `RDS Database Scanner`
   - Workspace: Select your workspace
4. Click **"Create App"**
5. In the left sidebar, click **"Incoming Webhooks"**
6. Toggle **"Activate Incoming Webhooks"** to ON
7. Click **"Add New Webhook to Workspace"**
8. Select the channel where you want notifications (e.g., `#database-alerts`)
9. Click **"Allow"**
10. **Copy the Webhook URL** - it looks like:
    ```
    https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
    ```

### Option B: Using Legacy Incoming Webhooks

1. Go to: https://YOUR-WORKSPACE.slack.com/apps/manage/custom-integrations
2. Click **"Incoming Webhooks"**
3. Click **"Add to Slack"**
4. Choose a channel and click **"Add Incoming WebHooks integration"**
5. **Copy the Webhook URL**

## Step 2: Prepare Parameters

Create a file `parameters.json` with your configuration:

```json
[
  {
    "ParameterKey": "SlackWebhookUrl",
    "ParameterValue": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  },
  {
    "ParameterKey": "ScanRegions",
    "ParameterValue": "us-east-1,us-west-2,eu-west-1"
  },
  {
    "ParameterKey": "MondaySchedule",
    "ParameterValue": "cron(0 9 ? * MON *)"
  },
  {
    "ParameterKey": "FridaySchedule",
    "ParameterValue": "cron(0 14 ? * FRI *)"
  },
  {
    "ParameterKey": "SlackChannel",
    "ParameterValue": ""
  },
  {
    "ParameterKey": "CpuThreshold",
    "ParameterValue": "50"
  },
  {
    "ParameterKey": "TransactionThreshold",
    "ParameterValue": "50"
  },
  {
    "ParameterKey": "ReportRetentionDays",
    "ParameterValue": "90"
  }
]
```

### Parameter Descriptions

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| **SlackWebhookUrl** | Your Slack incoming webhook URL | (required) | https://hooks.slack.com/services/... |
| **ScanRegions** | Comma-separated AWS regions | us-east-1,us-west-2 | us-east-1,us-west-2,eu-west-1 |
| **MondaySchedule** | Cron for Monday scans (UTC) | cron(0 9 ? * MON *) | 9 AM UTC every Monday |
| **FridaySchedule** | Cron for Friday scans (UTC) | cron(0 14 ? * FRI *) | 2 PM UTC every Friday |
| **SlackChannel** | Override default channel | "" | #database-alerts |
| **CpuThreshold** | CPU % for underused flag | 50 | Any value 0-100 |
| **TransactionThreshold** | Monthly transactions for underused | 50 | Any positive number |
| **ReportRetentionDays** | Days to keep S3 reports | 90 | 1-365 |

### Schedule Examples

```bash
# Every Monday at 9 AM UTC (4 AM EST, 1 AM PST)
cron(0 9 ? * MON *)

# Every Friday at 2 PM UTC (9 AM EST, 6 AM PST)
cron(0 14 ? * FRI *)

# Every Monday at 1 PM UTC (8 AM EST, 5 AM PST)
cron(0 13 ? * MON *)

# Multiple days: Monday and Friday at 10 AM UTC
# Note: You'll need separate rules - use existing Monday/Friday rules
```

## Step 3: Deploy CloudFormation Stack

### Using AWS Console

1. Go to **AWS CloudFormation Console**
2. Click **"Create stack"** → **"With new resources"**
3. Choose **"Upload a template file"**
4. Upload `rds-scanner-cloudformation.yaml`
5. Click **"Next"**
6. Enter:
   - **Stack name**: `rds-database-scanner`
   - Fill in all parameters (especially SlackWebhookUrl)
7. Click **"Next"** through remaining pages
8. Check **"I acknowledge that AWS CloudFormation might create IAM resources"**
9. Click **"Create stack"**

### Using AWS CLI

```bash
# Deploy the stack
aws cloudformation create-stack \
  --stack-name rds-database-scanner \
  --template-body file://rds-scanner-cloudformation.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Monitor deployment
aws cloudformation wait stack-create-complete \
  --stack-name rds-database-scanner \
  --region us-east-1

# View outputs
aws cloudformation describe-stacks \
  --stack-name rds-database-scanner \
  --region us-east-1 \
  --query 'Stacks[0].Outputs'
```

### Deployment Time

⏱️ **Expected duration**: 2-3 minutes

## Step 4: Test the Deployment

### Option A: Manual Trigger via Console

1. Go to **AWS Lambda Console**
2. Find function: `rds-scanner-{region}`
3. Click **"Test"** tab
4. Create test event:
   ```json
   {
     "scan_type": "manual_test",
     "scheduled": false
   }
   ```
5. Click **"Test"**
6. Check your Slack channel for the notification

### Option B: Manual Trigger via CLI

```bash
# Test the Lambda function
aws lambda invoke \
  --function-name rds-scanner-us-east-1 \
  --payload '{"scan_type":"manual_test"}' \
  --region us-east-1 \
  response.json

# View the response
cat response.json

# Check CloudWatch logs
aws logs tail /aws/lambda/rds-scanner-us-east-1 --follow
```

### Option C: Wait for Scheduled Execution

The function will automatically run:
- **Every Monday** at the scheduled time (with reminder pretext)
- **Every Friday** at the scheduled time (regular report)

## Step 5: Verify Everything Works

### Check CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/rds-scanner-us-east-1 --since 30m

# Follow logs in real-time
aws logs tail /aws/lambda/rds-scanner-us-east-1 --follow
```

### Check S3 Reports

```bash
# List generated reports
aws s3 ls s3://rds-scanner-reports-{ACCOUNT-ID}-{REGION}/rds-scans/

# Download latest report
aws s3 cp s3://rds-scanner-reports-{ACCOUNT-ID}-{REGION}/rds-scans/rds_scan_latest.json ./
```

### Check Slack Messages

Expected message format:

**Monday (with reminder):**
```
🔔 REMINDER: Weekly RDS Database Scan Results
Please review unused and underused databases for cost optimization.

📊 Summary:
• ❌ Unused: 5 databases (0 transactions in 6 months)
• ⚠️ Underused: 12 databases (low CPU or transactions)
• ✅ Active: 23 databases

💰 Potential Monthly Savings: ~$1,100

[Detailed list of databases...]

📋 Action Items:
• Review unused databases for deletion
• Consider downsizing underused databases
• Verify missing tags (Owner, Contact, Repo)
• Update team on cost optimization progress
```

**Friday (regular report):**
```
📊 RDS Database Scan Results - End of Week Report

[Same detailed information without reminder and action items]
```

## Update Configuration

### Update Slack Webhook

```bash
# Update the secret
aws secretsmanager update-secret \
  --secret-id rds-scanner-slack-webhook-us-east-1 \
  --secret-string '{"webhook_url":"https://hooks.slack.com/services/NEW/URL","channel":"#new-channel"}' \
  --region us-east-1
```

### Update Schedule

```bash
# Update parameters and stack
aws cloudformation update-stack \
  --stack-name rds-database-scanner \
  --template-body file://rds-scanner-cloudformation.yaml \
  --parameters file://updated-parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Update Scan Regions

Edit `parameters.json` and update the stack:

```json
{
  "ParameterKey": "ScanRegions",
  "ParameterValue": "us-east-1,us-west-2,eu-west-1,ap-southeast-1"
}
```

Then update:
```bash
aws cloudformation update-stack \
  --stack-name rds-database-scanner \
  --use-previous-template \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

## Monitoring and Troubleshooting

### Check Lambda Execution

```bash
# Recent invocations
aws lambda get-function \
  --function-name rds-scanner-us-east-1

# View metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=rds-scanner-us-east-1 \
  --start-time $(date -u -d '1 day ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum
```

### Common Issues

#### Issue: "Slack webhook returns 404"
**Solution**: 
- Verify webhook URL is correct
- Check if Slack app is still installed in workspace
- Recreate webhook if necessary

#### Issue: "No databases found"
**Solution**:
- Verify regions are correct
- Check IAM permissions
- Ensure RDS instances exist in specified regions

#### Issue: "Lambda timeout"
**Solution**:
- Increase timeout in CloudFormation (current: 900 seconds)
- Reduce number of regions scanned
- Scan regions separately

#### Issue: "Access Denied errors"
**Solution**:
- Check IAM role has all permissions from template
- Verify CloudWatch metrics are enabled for RDS
- Ensure cross-region permissions if scanning multiple regions

### View CloudWatch Alarms

```bash
# List all alarms
aws cloudwatch describe-alarms \
  --alarm-name-prefix rds-scanner

# Check alarm state
aws cloudwatch describe-alarm-history \
  --alarm-name rds-scanner-lambda-errors-us-east-1
```

## Cost Estimation

### Monthly Costs (Typical)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 8 executions/month × 5 min | ~$0.50 |
| CloudWatch Logs | 1 GB/month | ~$0.50 |
| S3 Storage | 100 MB | ~$0.01 |
| Secrets Manager | 1 secret | ~$0.40 |
| CloudWatch Metrics | Standard | Free Tier |
| **Total** | | **~$1.50/month** |

*Costs may vary based on number of databases and regions*

## Cleanup / Deletion

### Delete the Stack

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack \
  --stack-name rds-database-scanner \
  --region us-east-1

# Wait for deletion
aws cloudformation wait stack-delete-complete \
  --stack-name rds-database-scanner \
  --region us-east-1
```

### Manual Cleanup (if needed)

```bash
# Empty S3 bucket first
aws s3 rm s3://rds-scanner-reports-{ACCOUNT-ID}-{REGION}/ --recursive

# Then delete stack
aws cloudformation delete-stack --stack-name rds-database-scanner
```

## Multi-Account Deployment

To scan databases across multiple AWS accounts:

1. Deploy this stack in a **central monitoring account**
2. Set up **cross-account IAM roles** in each account
3. Update Lambda to assume roles for each account
4. See `multi-account-setup.md` for detailed instructions

## Advanced Customization

### Add Custom Metrics

Edit the Lambda function code to include additional CloudWatch metrics:
- `DatabaseConnections`
- `FreeableMemory`
- `FreeStorageSpace`
- `ReadLatency` / `WriteLatency`

### Customize Slack Message Format

Modify the `format_slack_message` function in Lambda to:
- Add more details
- Change color schemes
- Include graphs/charts (using Slack Block Kit)
- Add interactive buttons

### Add Email Notifications

Add SNS topic to CloudFormation and subscribe emails:

```yaml
EmailTopic:
  Type: AWS::SNS::Topic
  Properties:
    Subscription:
      - Endpoint: your-email@company.com
        Protocol: email
```

## Support and Resources

- **CloudFormation Documentation**: https://docs.aws.amazon.com/cloudformation/
- **Lambda Documentation**: https://docs.aws.amazon.com/lambda/
- **Slack API Documentation**: https://api.slack.com/messaging/webhooks
- **AWS RDS Metrics**: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/monitoring-cloudwatch.html

## Next Steps

1. ✅ Review first scan results in Slack
2. ✅ Tag untagged databases (Owner, Contact, Repo)
3. ✅ Archive or delete unused databases
4. ✅ Downsize underused databases
5. ✅ Set up cost tracking dashboard
6. ✅ Schedule team review meetings

---

**Need help?** Check CloudWatch Logs for detailed execution information.
