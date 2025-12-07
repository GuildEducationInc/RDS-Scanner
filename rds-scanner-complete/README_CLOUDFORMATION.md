# RDS Scanner - CloudFormation Deployment with Slack Integration

Complete AWS CloudFormation solution for automated RDS database scanning with Slack notifications.

## 🎯 What This Does

Automatically scans your AWS RDS databases and sends formatted reports to Slack:

- **📅 Scheduled Runs**: Every Monday and Friday at 9:00 AM UTC
- **⏰ Monday Reminder**: Includes a pretext reminder to review databases
- **💬 Slack Notifications**: Beautiful formatted messages with all findings
- **📊 Detailed Reports**: CSV files stored in S3
- **💰 Cost Insights**: Estimates potential monthly savings
- **🏷️ Tag Tracking**: Identifies databases missing owner, contact, and repo tags

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `rds-scanner-cloudformation.yaml` | Main CloudFormation template |
| `parameters.json` | Configuration parameters |
| `deploy.sh` | Automated deployment script |
| `CFT_DEPLOYMENT_GUIDE.md` | Detailed deployment instructions |
| `SLACK_MESSAGE_EXAMPLES.md` | Visual examples of Slack messages |

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- AWS CLI installed and configured
- Slack webhook URL (see [Setup Guide](#slack-webhook-setup))
- AWS account with appropriate permissions

### Deploy in 3 Steps

**Step 1: Get Your Slack Webhook**
1. Go to https://api.slack.com/messaging/webhooks
2. Create new webhook → Select channel
3. Copy the webhook URL

**Step 2: Run Deployment Script**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Step 3: Test It**
```bash
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": true}' \
  response.json
```

Check your Slack channel! 🎉

## 📋 What Gets Deployed

### AWS Resources

```
┌─────────────────────────────────────────────────────────┐
│  EventBridge Rules (Monday + Friday)                    │
│             ↓                                           │
│  Lambda Function (Python 3.9)                           │
│             ↓                                           │
│  Scans RDS + CloudWatch Metrics                         │
│             ↓                                           │
│  Stores Reports in S3                                   │
│             ↓                                           │
│  Sends Notifications to Slack                           │
└─────────────────────────────────────────────────────────┘
```

**Created Resources:**
- ✅ Lambda Function (rds-scanner-function)
- ✅ IAM Role with required permissions
- ✅ S3 Bucket for reports (with lifecycle policy)
- ✅ CloudWatch Log Group
- ✅ EventBridge Rules (2: Monday & Friday)

**Estimated Cost:** ~$1-2/month

## 🎛️ Configuration

### Default Settings

| Setting | Value | Customizable |
|---------|-------|--------------|
| **Schedule** | Mon & Fri 9AM UTC | ✅ Yes |
| **CPU Threshold** | 50% | ✅ Yes |
| **Transaction Threshold** | 50/month | ✅ Yes |
| **Report Retention** | 90 days | ✅ Yes |
| **Lambda Timeout** | 15 minutes | ✅ Yes |
| **Lambda Memory** | 512 MB | ✅ Yes |

### Customize Parameters

Edit `parameters.json` before deployment:

```json
{
  "ParameterKey": "ScanRegions",
  "ParameterValue": "us-east-1,us-west-2,eu-west-1"
},
{
  "ParameterKey": "CPUThreshold",
  "ParameterValue": "40"
},
{
  "ParameterKey": "TransactionThreshold",
  "ParameterValue": "100"
}
```

## 📱 Slack Integration

### Message Schedule

- **Monday 9:00 AM UTC**: Full report with ⏰ REMINDER pretext
- **Friday 9:00 AM UTC**: Regular status update

### What's in the Message?

✅ Total database count  
✅ Unused databases (0 transactions in 6 months)  
✅ Underused databases (CPU < 50% OR transactions < 50/month)  
✅ Potential monthly savings estimate  
✅ Top 5 unused databases with owners  
✅ Top 5 underused databases with metrics  
✅ Link to full CSV report in S3  

See [SLACK_MESSAGE_EXAMPLES.md](SLACK_MESSAGE_EXAMPLES.md) for visual examples!

### Slack Webhook Setup

**Method 1: Create New Webhook**
1. Visit: https://api.slack.com/messaging/webhooks
2. Click "Create your Slack app"
3. Choose "From scratch"
4. Name: "RDS Scanner"
5. Select workspace
6. Enable "Incoming Webhooks"
7. "Add New Webhook to Workspace"
8. Select channel (e.g., #database-ops)
9. Copy webhook URL

**Method 2: Use Existing Webhook**
If you already have webhooks enabled, just copy the URL.

**Webhook URL Format:**
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

## 🔧 Deployment Methods

### Method 1: Automated Script (Recommended)

```bash
./deploy.sh
```

The script will:
- Validate the template
- Prompt for Slack webhook
- Ask for regions to scan
- Create parameters file
- Deploy the stack
- Wait for completion
- Offer to test immediately

### Method 2: AWS CLI

```bash
aws cloudformation create-stack \
  --stack-name rds-scanner \
  --template-body file://rds-scanner-cloudformation.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Method 3: AWS Console

1. Open CloudFormation console
2. Create Stack → Upload template
3. Upload `rds-scanner-cloudformation.yaml`
4. Fill in parameters
5. Acknowledge IAM capabilities
6. Create stack

## 📊 Understanding the Scan

### Database Categories

**Unused** 🔴
- Zero transactions in last 6 months
- Calculated from Read IOPS + Write IOPS
- **Action**: Consider deleting or archiving

**Underused** 🟡
- CPU utilization < 50% (6-month average) **OR**
- Transactions < 50 per month
- **Action**: Consider downsizing instance class

**Active** 🟢
- Everything else
- No action needed

### Metrics Used

| Metric | Source | Purpose |
|--------|--------|---------|
| CPU Utilization | CloudWatch | Identify low-usage databases |
| Read IOPS | CloudWatch | Measure read activity |
| Write IOPS | CloudWatch | Measure write activity |
| Database Tags | RDS API | Owner accountability |

### Tag Requirements

For best results, tag your databases:

```bash
aws rds add-tags-to-resource \
  --resource-name arn:aws:rds:region:account:db:dbname \
  --tags \
    Key=Owner,Value=john@company.com \
    Key=Contact,Value=john@company.com \
    Key=Repo,Value=github.com/myorg/myrepo \
    Key=Environment,Value=production
```

## 📈 Monitoring & Management

### View Lambda Logs

```bash
# Follow logs in real-time
aws logs tail /aws/lambda/rds-scanner-function --follow

# View last hour
aws logs tail /aws/lambda/rds-scanner-function --since 1h
```

### Check Stack Status

```bash
aws cloudformation describe-stacks --stack-name rds-scanner
```

### List S3 Reports

```bash
aws s3 ls s3://rds-scanner-reports-YOUR-ACCOUNT-ID/rds-scans/
```

### Download Latest Report

```bash
aws s3 cp s3://rds-scanner-reports-YOUR-ACCOUNT-ID/rds-scans/ ./ --recursive --exclude "*" --include "rds_scan_*" --exclude "*" --include "$(aws s3 ls s3://rds-scanner-reports-YOUR-ACCOUNT-ID/rds-scans/ | tail -1 | awk '{print $4}')"
```

### Manually Trigger Scan

```bash
# Test with Monday reminder
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": true}' \
  response.json

# Test without reminder
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": false}' \
  response.json
```

## 🔄 Updating the Stack

### Update Slack Webhook Only

```bash
aws cloudformation update-stack \
  --stack-name rds-scanner \
  --use-previous-template \
  --parameters \
    ParameterKey=SlackWebhookURL,ParameterValue=NEW_WEBHOOK_URL \
    ParameterKey=ScanRegions,UsePreviousValue=true \
    ParameterKey=ProjectName,UsePreviousValue=true \
    ParameterKey=LambdaTimeout,UsePreviousValue=true \
    ParameterKey=LambdaMemorySize,UsePreviousValue=true \
    ParameterKey=ReportRetentionDays,UsePreviousValue=true \
    ParameterKey=CPUThreshold,UsePreviousValue=true \
    ParameterKey=TransactionThreshold,UsePreviousValue=true \
  --capabilities CAPABILITY_NAMED_IAM
```

### Update All Parameters

Edit `parameters.json` and run:
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

## 🛠️ Troubleshooting

### Stack Creation Fails

**Validate template:**
```bash
aws cloudformation validate-template \
  --template-body file://rds-scanner-cloudformation.yaml
```

**Check events:**
```bash
aws cloudformation describe-stack-events \
  --stack-name rds-scanner \
  --max-items 20
```

### No Slack Messages

1. **Test webhook manually:**
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test"}' \
  YOUR_WEBHOOK_URL
```

2. **Check Lambda logs:**
```bash
aws logs tail /aws/lambda/rds-scanner-function --follow
```

3. **Verify environment variables:**
```bash
aws lambda get-function-configuration \
  --function-name rds-scanner-function
```

### Lambda Timeout

Increase timeout in `parameters.json`:
```json
{
  "ParameterKey": "LambdaTimeout",
  "ParameterValue": "900"
}
```

### Missing CloudWatch Metrics

- Enable Enhanced Monitoring on RDS instances
- Wait 24-48 hours for metrics to populate
- Verify correct regions are being scanned

## 🧹 Cleanup

### Delete Everything

```bash
# Empty S3 bucket first
aws s3 rm s3://rds-scanner-reports-YOUR-ACCOUNT-ID --recursive

# Delete stack
aws cloudformation delete-stack --stack-name rds-scanner

# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name rds-scanner
```

## 💰 Cost Analysis

### Monthly AWS Costs

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 8 invocations/month @ 15min each | ~$0.50 |
| S3 | Storage for reports | ~$0.10 |
| CloudWatch Logs | Log retention | ~$0.50 |
| CloudWatch API | Metrics calls | Free tier |
| EventBridge | Scheduled rules | Free |
| **Total** | | **~$1-2/month** |

### Potential Savings

**Example Scenarios:**

| Organization Size | Unused DBs | Monthly Savings |
|------------------|------------|-----------------|
| Small Team | 3-5 databases | $300-$500 |
| Medium Company | 10-15 databases | $1,000-$2,000 |
| Enterprise | 20+ databases | $5,000-$10,000+ |

**ROI**: 500-10,000x 🎯

## 📚 Additional Resources

- **Detailed Guide**: [CFT_DEPLOYMENT_GUIDE.md](CFT_DEPLOYMENT_GUIDE.md)
- **Slack Examples**: [SLACK_MESSAGE_EXAMPLES.md](SLACK_MESSAGE_EXAMPLES.md)
- **AWS CloudFormation**: https://docs.aws.amazon.com/cloudformation/
- **Slack Webhooks**: https://api.slack.com/messaging/webhooks

## 🤝 Support

### Common Issues

1. **Permissions**: Ensure IAM user has CloudFormation, Lambda, S3, IAM permissions
2. **Slack**: Verify webhook URL format and channel access
3. **Regions**: Confirm databases exist in specified regions
4. **Tags**: Add required tags to databases for better reporting

### Getting Help

- Check CloudWatch Logs
- Review CloudFormation events
- Test components individually
- Verify IAM permissions

## ✅ Next Steps

1. ✅ Deploy using `./deploy.sh`
2. ✅ Test Lambda function
3. ✅ Check Slack message
4. ✅ Review first report
5. ✅ Tag untagged databases
6. ✅ Take action on unused databases
7. ✅ Monitor weekly reports
8. ✅ Track cost savings

---

**Ready to save costs and optimize your database fleet?**

Run: `./deploy.sh` 🚀

For detailed instructions, see [CFT_DEPLOYMENT_GUIDE.md](CFT_DEPLOYMENT_GUIDE.md)
