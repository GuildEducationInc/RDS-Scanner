# Slack Integration - Quick Reference

## 🚀 Quick Setup (5 Minutes)

### 1. Create Slack Webhook
1. Go to: https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: `RDS Database Scanner`
4. Enable "Incoming Webhooks" → ON
5. "Add New Webhook to Workspace" → Select channel
6. Copy webhook URL (looks like `https://hooks.slack.com/services/...`)

### 2. Test Webhook
```bash
python3 slack_notifier.py "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### 3. Use with Scanner

#### Local Execution
```bash
python3 rds_scanner.py \
  --profiles dev stage prod \
  --regions us-east-1 us-west-2 \
  --slack-webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

#### Lambda Deployment
```bash
aws lambda update-function-configuration \
  --function-name rds-database-scanner \
  --environment Variables="{
    REGIONS=us-east-1,us-west-2,
    S3_BUCKET=your-bucket,
    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
  }"
```

#### Terraform
```hcl
# terraform.tfvars
slack_webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
schedule_expression = "cron(0 9 ? * MON *)"  # Every Monday 9 AM UTC
```

## 📅 Schedule Options

```bash
# Every Monday at 9 AM UTC (default)
cron(0 9 ? * MON *)

# Daily at 9 AM UTC
cron(0 9 * * ? *)

# First day of month
cron(0 8 1 * ? *)

# Every weekday
cron(0 10 ? * MON-FRI *)
```

## 📊 What Appears in Slack

```
🔍 RDS Database Scan Results
Scan Date: 2024-12-09 09:00 UTC
Total Databases: 47

🔴 Unused: 23        🟡 Underused: 15
🟢 Active: 9         💰 Savings: ~$4,500/mo

🔴 Unused Databases (0 transactions in 6 months)
• legacy-mysql-prod (mysql, db.t3.medium)
  Owner: john@company.com | Env: prod

🟡 Underused Databases
• reporting-db (CPU: 12.34%; Transactions: 28/mo)
  Owner: reports@company.com | Env: prod

📋 Recommended Actions:
• Delete 23 unused databases
• Downsize 15 underused databases

📊 Download Full CSV Report
```

## 🔧 Common Commands

```bash
# Test Slack webhook only
python3 slack_notifier.py "YOUR_WEBHOOK_URL"

# Scan with Slack notification
python3 rds_scanner.py --slack-webhook "YOUR_WEBHOOK_URL"

# Trigger Lambda immediately
aws lambda invoke --function-name rds-database-scanner response.json

# View Lambda logs
aws logs tail /aws/lambda/rds-database-scanner --follow

# Update Lambda webhook
aws lambda update-function-configuration \
  --function-name rds-database-scanner \
  --environment Variables="{SLACK_WEBHOOK_URL=NEW_URL}"
```

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| 404 error | Webhook URL invalid - recreate in Slack |
| 403 error | Webhook revoked - create new webhook |
| No message | Install requests: `pip install requests` |
| No formatting | Check Slack blocks syntax |
| Lambda timeout | Increase timeout to 900 seconds |

## 🔐 Security Tips

✅ **DO:**
- Store webhook in environment variables
- Use AWS Secrets Manager for production
- Create separate webhooks for dev/prod
- Rotate webhook if exposed

❌ **DON'T:**
- Commit webhook URL to Git
- Share webhook URL publicly
- Use same webhook across environments

## 📚 Full Documentation

- Complete setup: [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)
- Lambda deployment: [LAMBDA_DEPLOYMENT.md](LAMBDA_DEPLOYMENT.md)
- Scanner usage: [README.md](README.md)

## 💰 Cost

- Lambda: ~$0.50/month
- Slack: Free
- **Total: ~$0.50/month**
- **Potential savings: $500-$5,000+/month**

---

**Need help?** See full guide: [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)
