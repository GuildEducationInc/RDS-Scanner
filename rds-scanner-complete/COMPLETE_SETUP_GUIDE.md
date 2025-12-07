# Complete Setup Guide - RDS Scanner with Slack Integration

## Overview

This guide walks you through setting up automated weekly Slack notifications for your RDS database scans every Monday.

**What you'll achieve:**
- Automated RDS scanning across all environments
- Rich Slack notifications with cost estimates
- Weekly reports every Monday at 9 AM
- Complete visibility into unused and underused databases

**Time to complete:** 30 minutes

---

## Part 1: Setup Slack (10 minutes)

### Step 1: Create Slack Incoming Webhook

1. **Go to Slack API**: https://api.slack.com/apps
2. **Create New App**:
   - Click "Create New App" → "From scratch"
   - App Name: `RDS Database Scanner`
   - Select your workspace
   - Click "Create App"

3. **Enable Incoming Webhooks**:
   - Left sidebar → "Incoming Webhooks"
   - Toggle to **ON**
   - Scroll down → "Add New Webhook to Workspace"
   - Select channel (e.g., `#cloud-ops`, `#database-alerts`)
   - Click "Allow"

4. **Copy Webhook URL**:
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
   ```
   **⚠️ Keep this secure!**

### Step 2: Test Slack Integration

```bash
# Test your webhook
python3 slack_notifier.py "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

You should see a test message in your Slack channel! ✅

---

## Part 2: Local Testing (5 minutes)

Test the scanner locally before deploying to Lambda:

```bash
# Install dependencies
pip install boto3 requests

# Run a test scan with Slack notification
python3 rds_scanner.py \
  --profiles dev \
  --regions us-east-1 \
  --slack-webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

Check your Slack channel for the scan results! 🎉

---

## Part 3: Deploy to AWS Lambda (15 minutes)

### Option A: Using AWS CLI

#### 1. Create S3 Bucket for Reports
```bash
aws s3 mb s3://rds-scanner-reports-YOUR_ACCOUNT_ID
```

#### 2. Create IAM Role
```bash
# Create trust policy
cat > lambda-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name RDSScannerLambdaRole \
  --assume-role-policy-document file://lambda-trust-policy.json

# Attach permissions (use iam_policy.json)
aws iam put-role-policy \
  --role-name RDSScannerLambdaRole \
  --policy-name RDSScannerExecutionPolicy \
  --policy-document file://iam_policy.json
```

#### 3. Package Lambda Function
```bash
# Create package directory
mkdir lambda_package
cd lambda_package

# Copy files
cp ../rds_scanner.py .
cp ../slack_notifier.py .
cp ../lambda_handler.py .

# Install dependencies
pip install boto3 requests -t .

# Create zip
zip -r ../rds_scanner_lambda.zip .
cd ..
```

#### 4. Create Lambda Function
```bash
aws lambda create-function \
  --function-name rds-database-scanner \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/RDSScannerLambdaRole \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://rds_scanner_lambda.zip \
  --timeout 900 \
  --memory-size 512 \
  --environment Variables="{
    REGIONS=us-east-1,us-west-2,
    S3_BUCKET=rds-scanner-reports-YOUR_ACCOUNT_ID,
    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
  }"
```

#### 5. Create Schedule (Every Monday at 9 AM UTC)
```bash
# Create CloudWatch Events rule
aws events put-rule \
  --name rds-scanner-weekly \
  --schedule-expression "cron(0 9 ? * MON *)" \
  --description "Run RDS scanner every Monday"

# Add Lambda permission
aws lambda add-permission \
  --function-name rds-database-scanner \
  --statement-id rds-scanner-weekly-event \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:YOUR_ACCOUNT_ID:rule/rds-scanner-weekly

# Add Lambda as target
aws events put-targets \
  --rule rds-scanner-weekly \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:rds-database-scanner"
```

#### 6. Test Lambda
```bash
# Trigger immediately
aws lambda invoke \
  --function-name rds-database-scanner \
  response.json

# View response
cat response.json

# Check logs
aws logs tail /aws/lambda/rds-database-scanner --follow
```

### Option B: Using Terraform

#### 1. Create terraform.tfvars
```hcl
aws_region         = "us-east-1"
scan_regions       = "us-east-1,us-west-2"
email_address      = "cloud-ops@company.com"
slack_webhook_url  = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
schedule_expression = "cron(0 9 ? * MON *)"
```

#### 2. Deploy
```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy
terraform apply
```

Done! Terraform creates:
- ✅ S3 bucket for reports
- ✅ Lambda function with all dependencies
- ✅ IAM roles and permissions
- ✅ CloudWatch Events schedule
- ✅ All necessary integrations

---

## Part 4: Verify Everything Works

### Test 1: Trigger Lambda Manually
```bash
aws lambda invoke \
  --function-name rds-database-scanner \
  response.json

# Check Slack - you should see a message!
```

### Test 2: Check Logs
```bash
aws logs tail /aws/lambda/rds-database-scanner --follow
```

### Test 3: Verify Schedule
```bash
aws events list-rules --name-prefix rds-scanner
```

---

## What You'll See in Slack Every Monday

```
🔍 RDS Database Scan Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scan Date: 2024-12-09 09:00 UTC
Total Databases Scanned: 47

┌─────────────────────────────────┐
│ 🔴 Unused: 23  │ 🟡 Underused: 15 │
│ 🟢 Active: 9   │ 💰 Savings: $4.5K │
└─────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 Unused Databases (0 transactions in 6 months)

• legacy-mysql-prod
  Engine: mysql | Instance: db.t3.medium
  Owner: john.doe@company.com
  Contact: team-data | Environment: prod

• old-analytics-db
  Engine: postgres | Instance: db.m5.large
  Owner: analytics@company.com
  Contact: data-team | Environment: stage

...and 21 more unused databases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 Underused Databases (CPU < 50% or low activity)

• reporting-db
  CPU: 12.34%; Transactions/month: 28
  Owner: reports@company.com
  Contact: bi-team | Environment: prod

...and 14 more underused databases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Recommended Actions:
• Review and delete 23 unused database(s)
• Consider downsizing 15 underused database(s)

📊 Download Full CSV Report
```

---

## Customization Options

### Change Schedule

Edit schedule in CloudWatch Events or Terraform:

```bash
# Daily at 9 AM UTC
cron(0 9 * * ? *)

# Every Monday at 9 AM UTC (default)
cron(0 9 ? * MON *)

# First day of month
cron(0 8 1 * ? *)

# Twice per week (Monday & Thursday)
cron(0 9 ? * MON,THU *)
```

### Add More Regions

```bash
aws lambda update-function-configuration \
  --function-name rds-database-scanner \
  --environment Variables="{
    REGIONS=us-east-1,us-west-2,eu-west-1,ap-southeast-1,
    S3_BUCKET=your-bucket,
    SLACK_WEBHOOK_URL=your-webhook
  }"
```

### Send to Different Slack Channel

1. Create new webhook in Slack for different channel
2. Update Lambda environment variable with new webhook URL

### Customize Cost Estimates

Edit `slack_notifier.py` method `_estimate_savings()` to match your actual costs

---

## Maintenance

### Update Lambda Function
```bash
# Make code changes
# Re-package
cd lambda_package
zip -r ../rds_scanner_lambda.zip .
cd ..

# Update Lambda
aws lambda update-function-code \
  --function-name rds-database-scanner \
  --zip-file fileb://rds_scanner_lambda.zip
```

### Rotate Slack Webhook
```bash
# Create new webhook in Slack
# Update Lambda
aws lambda update-function-configuration \
  --function-name rds-database-scanner \
  --environment Variables="{
    REGIONS=...,
    S3_BUCKET=...,
    SLACK_WEBHOOK_URL=NEW_WEBHOOK_URL
  }"
```

### View Historical Reports
```bash
# List S3 reports
aws s3 ls s3://your-bucket/rds-scans/

# Download specific report
aws s3 cp s3://your-bucket/rds-scans/rds_scan_20241209_090000.csv .
```

---

## Troubleshooting

### ❌ No Slack Message
- Check Lambda logs: `aws logs tail /aws/lambda/rds-database-scanner`
- Verify webhook URL is correct
- Test webhook: `python3 slack_notifier.py "YOUR_WEBHOOK"`

### ❌ Lambda Timeout
- Increase timeout: `--timeout 900`
- Check CloudWatch Logs for errors

### ❌ Missing Databases
- Verify correct regions configured
- Check IAM permissions in `iam_policy.json`
- Ensure RDS instances exist

### ❌ Wrong Cost Estimates
- Customize `_estimate_savings()` in `slack_notifier.py`
- Based on your actual RDS pricing

---

## Cost Summary

| Component | Monthly Cost |
|-----------|-------------|
| Lambda execution | ~$0.50 |
| S3 storage | ~$0.02 |
| CloudWatch | Free tier |
| Slack | Free |
| **Total** | **~$0.52/month** |

**Potential Savings from Optimization:** $500 - $5,000+/month 💰

---

## Next Steps

1. ✅ Review first Monday report
2. ✅ Tag databases missing owner/contact
3. ✅ Delete or archive unused databases
4. ✅ Downsize underused databases
5. ✅ Track savings over time
6. ✅ Share results with leadership

---

## Quick Reference

**Test Slack:**
```bash
python3 slack_notifier.py "YOUR_WEBHOOK_URL"
```

**Trigger Lambda Now:**
```bash
aws lambda invoke --function-name rds-database-scanner response.json
```

**View Logs:**
```bash
aws logs tail /aws/lambda/rds-database-scanner --follow
```

**List Reports:**
```bash
aws s3 ls s3://your-bucket/rds-scans/
```

---

## Documentation

- **Complete Guide**: [README.md](README.md)
- **Slack Setup**: [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)
- **Quick Reference**: [SLACK_QUICKREF.md](SLACK_QUICKREF.md)
- **Lambda Details**: [LAMBDA_DEPLOYMENT.md](LAMBDA_DEPLOYMENT.md)
- **5-Min Start**: [QUICKSTART.md](QUICKSTART.md)

---

**🎉 Congratulations!** You now have automated weekly RDS reports in Slack every Monday!

Your team will receive actionable insights on database optimization, and you'll be on your way to significant cost savings.

Questions? Check the troubleshooting section or review the detailed guides above.
