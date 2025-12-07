# RDS Database Scanner - CloudFormation Edition

## 🎯 Complete Automated Solution

Serverless RDS database scanner with **Slack integration** that automatically runs:
- **Every Monday at 9 AM UTC** - With reminder pretext and action items
- **Every Friday at 2 PM UTC** - Regular end-of-week report

## 📋 What It Does

Automatically scans your AWS RDS instances across all environments and identifies:

1. **❌ Unused Databases** - Zero transactions in the last 6 months
2. **⚠️ Underused Databases** - CPU < 50% OR transactions < 50/month  
3. **📊 Cost Savings** - Potential monthly savings estimate
4. **🏷️ Tags** - Extracts owner, contact, and repo tags

Results are sent to **Slack** with formatted messages and saved to **S3**.

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Get Your Slack Webhook (2 minutes)

1. Go to https://api.slack.com/apps
2. Create a new app → "From scratch"
3. Enable "Incoming Webhooks"
4. Add webhook to your channel (#database-alerts)
5. Copy the webhook URL

### Step 2: Configure Parameters (1 minute)

Edit `parameters.json`:

```json
{
  "ParameterKey": "SlackWebhookUrl",
  "ParameterValue": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
},
{
  "ParameterKey": "ScanRegions",
  "ParameterValue": "us-east-1,us-west-2"
}
```

### Step 3: Deploy (2 minutes)

```bash
# Make deploy script executable
chmod +x deploy.sh

# Deploy the stack
./deploy.sh
```

**Or use AWS CLI directly:**

```bash
aws cloudformation create-stack \
  --stack-name rds-database-scanner \
  --template-body file://rds-scanner-cloudformation.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

## 📁 Files Included

### Core Deployment
- **rds-scanner-cloudformation.yaml** - Complete CloudFormation template
- **parameters.json** - Configuration file
- **deploy.sh** - Automated deployment script

### Documentation
- **CLOUDFORMATION_DEPLOYMENT.md** - Detailed deployment guide
- **SLACK_INTEGRATION.md** - Slack message examples and customization
- **README.md** - This file

## 📊 Slack Notifications

### Monday Message (with reminder)
```
🔔 REMINDER: Weekly RDS Database Scan Results
Please review unused and underused databases for cost optimization.

Summary:
• ❌ Unused: 7 databases (0 transactions in 6 months)
• ⚠️ Underused: 15 databases (low CPU or transactions)
• ✅ Active: 18 databases
💰 Potential Monthly Savings: ~$1,450

📋 Action Items:
• Review unused databases for deletion
• Consider downsizing underused databases
• Verify missing tags (Owner, Contact, Repo)
• Update team on cost optimization progress
```

### Friday Message (regular report)
```
📊 RDS Database Scan Results - End of Week Report

Summary:
• ❌ Unused: 5 databases
• ⚠️ Underused: 13 databases
• ✅ Active: 20 databases
💰 Potential Monthly Savings: ~$1,150
```

See [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) for full message examples.

## ⚙️ Configuration Options

### Schedule Times

Edit in `parameters.json`:

```json
{
  "ParameterKey": "MondaySchedule",
  "ParameterValue": "cron(0 9 ? * MON *)"  // 9 AM UTC every Monday
},
{
  "ParameterKey": "FridaySchedule", 
  "ParameterValue": "cron(0 14 ? * FRI *)"  // 2 PM UTC every Friday
}
```

**Time Zone Reference:**
- `cron(0 9 ? * MON *)` = 9 AM UTC = 4 AM EST = 1 AM PST
- `cron(0 13 ? * MON *)` = 1 PM UTC = 8 AM EST = 5 AM PST
- `cron(0 14 ? * FRI *)` = 2 PM UTC = 9 AM EST = 6 AM PST

### Scan Regions

```json
{
  "ParameterKey": "ScanRegions",
  "ParameterValue": "us-east-1,us-west-2,eu-west-1,ap-southeast-1"
}
```

### Thresholds

```json
{
  "ParameterKey": "CpuThreshold",
  "ParameterValue": "50"  // Flag databases with CPU < 50%
},
{
  "ParameterKey": "TransactionThreshold",
  "ParameterValue": "50"  // Flag databases with < 50 transactions/month
}
```

## 🧪 Testing

### Manual Test

```bash
# Trigger a test scan
aws lambda invoke \
  --function-name rds-scanner-us-east-1 \
  --payload '{"scan_type":"manual_test"}' \
  response.json

# Check the result
cat response.json

# View logs
aws logs tail /aws/lambda/rds-scanner-us-east-1 --follow
```

### Check Slack Channel

After triggering, check your configured Slack channel for the notification.

### View S3 Reports

```bash
# List reports
aws s3 ls s3://rds-scanner-reports-{ACCOUNT-ID}-us-east-1/rds-scans/

# Download latest report
aws s3 cp s3://rds-scanner-reports-{ACCOUNT-ID}-us-east-1/rds-scans/rds_scan_latest.json ./
```

## 📦 What Gets Created

The CloudFormation stack creates:

- **Lambda Function** - Scans RDS instances and sends to Slack
- **IAM Role** - Permissions for RDS, CloudWatch, S3, Secrets Manager
- **S3 Bucket** - Stores detailed scan reports
- **Secrets Manager Secret** - Securely stores Slack webhook
- **EventBridge Rules** - Schedules for Monday and Friday
- **CloudWatch Log Group** - Lambda execution logs
- **CloudWatch Alarm** - Alerts on Lambda errors

## 💰 Cost Estimate

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Lambda | 8 executions × 5 min | ~$0.50 |
| S3 Storage | 100 MB | ~$0.01 |
| Secrets Manager | 1 secret | ~$0.40 |
| CloudWatch Logs | 1 GB | ~$0.50 |
| **Total** | | **~$1.50/month** |

**Potential Savings**: $500-$5,000/month from identifying unused/underused databases!

## 🔄 Update Stack

To update configuration:

```bash
# Edit parameters.json with new values

# Update the stack
aws cloudformation update-stack \
  --stack-name rds-database-scanner \
  --template-body file://rds-scanner-cloudformation.yaml \
  --parameters file://parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

Or use the deployment script:
```bash
./deploy.sh  # Will detect existing stack and offer to update
```

## 🗑️ Cleanup

To remove everything:

```bash
# Delete the stack
aws cloudformation delete-stack \
  --stack-name rds-database-scanner \
  --region us-east-1

# Note: S3 bucket must be empty first
aws s3 rm s3://rds-scanner-reports-{ACCOUNT-ID}-us-east-1/ --recursive
```

## 🛠️ Architecture

```
EventBridge Rules (Monday/Friday)
         ↓
    Lambda Function
         ↓
    ┌────┴────┬────────┬──────────┐
    ↓         ↓        ↓          ↓
  RDS API  CloudWatch S3 Bucket  Slack
                               Webhook
```

## 📚 Documentation

- **[CLOUDFORMATION_DEPLOYMENT.md](CLOUDFORMATION_DEPLOYMENT.md)** - Complete deployment guide
- **[SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)** - Slack setup and message examples
- **[parameters.json](parameters.json)** - Configuration template

## 🔐 Security

- ✅ Slack webhook stored in AWS Secrets Manager (encrypted)
- ✅ Least-privilege IAM permissions
- ✅ S3 bucket with encryption enabled
- ✅ No database credentials stored
- ✅ Read-only access to RDS and CloudWatch

## 🎓 Best Practices

1. **Tag Your Databases** - Add Owner, Contact, and Repo tags
2. **Review Weekly** - Act on Monday reminders
3. **Track Savings** - Monitor cost reduction over time
4. **Update Thresholds** - Adjust based on your workload patterns
5. **Test First** - Run manual test before waiting for scheduled scans

## 🆘 Troubleshooting

### No Slack Messages

1. Check CloudWatch Logs: `/aws/lambda/rds-scanner-{region}`
2. Verify webhook URL in Secrets Manager
3. Test Lambda manually
4. Check EventBridge rules are enabled

### Wrong Schedule Time

Remember schedules are in **UTC**. Convert to your timezone:
- 9 AM UTC = 4 AM EST = 1 AM PST
- Add hours to shift later: `cron(0 13 ? * MON *)` = 1 PM UTC = 8 AM EST

### Access Denied Errors

Verify IAM role has all required permissions from template.

### No Databases Found

1. Check `ScanRegions` parameter includes correct regions
2. Verify RDS instances exist in those regions
3. Check IAM permissions for RDS DescribeDBInstances

## 📊 Sample Output

**Typical scan results for 40 databases:**
- Unused: 7 databases → $700/month savings
- Underused: 15 databases → $750/month savings
- **Total potential savings: $1,450/month**

## 🎯 Next Steps

1. ✅ Deploy the stack (5 minutes)
2. ✅ Test with manual trigger
3. ✅ Wait for Monday/Friday or trigger manually
4. ✅ Review findings in Slack
5. ✅ Take action on unused/underused databases
6. ✅ Track your cost savings!

## 📞 Support

- **CloudWatch Logs**: Check Lambda execution logs
- **AWS Documentation**: See links in deployment guide
- **Slack API**: https://api.slack.com/messaging/webhooks

---

**Ready to save money on your RDS fleet?** 

Deploy now: `./deploy.sh` 🚀
