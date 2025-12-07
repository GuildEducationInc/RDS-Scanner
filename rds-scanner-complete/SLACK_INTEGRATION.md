# Slack Integration Guide

## 📱 Slack Message Examples

### Monday Message (With Reminder) 🔔

When the scanner runs on Monday, it sends a message with **reminder pretext** in **orange color**:

```
🔔 REMINDER: Weekly RDS Database Scan Results
Please review unused and underused databases for cost optimization.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗄️ RDS Database Scan Results

Scan Date: 2024-12-09 09:00 UTC
Total Databases: 40

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
• ❌ Unused: 7 databases (0 transactions in 6 months)
• ⚠️ Underused: 15 databases (low CPU or transactions)
• ✅ Active: 18 databases

💰 Potential Monthly Savings: ~$1,450

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ Unused Databases (7):

• `legacy-db-2019` (postgres, db.t3.medium)
  Region: us-east-1 | Owner: john.doe@company.com

• `old-staging-mysql` (mysql, db.t3.small)
  Region: us-west-2 | Owner: N/A

• `test-analytics-db` (aurora-postgresql, db.r5.large)
  Region: us-east-1 | Owner: data-team@company.com

... and 4 more unused databases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Underused Databases (15):

• `dev-api-db` (postgres, db.t3.large)
  Region: us-east-1 | CPU: 12.3%; Transactions: 23/month | Owner: api-team@company.com

• `reporting-db` (mysql, db.r5.xlarge)
  Region: us-west-2 | CPU: 8.5%; Transactions: 15/month | Owner: reports@company.com

• `backup-analytics` (aurora-mysql, db.t3.medium)
  Region: eu-west-1 | CPU: 45.2%; Transactions: 38/month | Owner: analytics@company.com

... and 12 more underused databases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Action Items:
• Review unused databases for deletion
• Consider downsizing underused databases
• Verify missing tags (Owner, Contact, Repo)
• Update team on cost optimization progress

📁 Full report: s3://rds-scanner-reports-123456789012-us-east-1/rds-scans/rds_scan_20241209_090000.json
```

### Friday Message (Regular Report) 📊

When the scanner runs on Friday, it sends a **regular report** in **green color** without reminder:

```
📊 RDS Database Scan Results - End of Week Report

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗄️ RDS Database Scan Results

Scan Date: 2024-12-13 14:00 UTC
Total Databases: 38

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
• ❌ Unused: 5 databases (0 transactions in 6 months)
• ⚠️ Underused: 13 databases (low CPU or transactions)
• ✅ Active: 20 databases

💰 Potential Monthly Savings: ~$1,150

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Same detailed database listings...]

📁 Full report: s3://rds-scanner-reports-123456789012-us-east-1/rds-scans/rds_scan_20241213_140000.json
```

## 🎨 Message Features

### Visual Elements

- **Emojis**: Used for quick visual scanning
- **Color Coding**: Orange (Monday reminder) vs Green (Friday report)
- **Formatting**: Bold headers, inline code, bullet points
- **Action Items**: (Monday only) Specific next steps

### Information Hierarchy

1. Header: Scan type and date
2. Summary: High-level metrics and savings
3. Unused Databases: Critical findings
4. Underused Databases: Optimization opportunities
5. Action Items: (Monday only) Next steps
6. S3 Link: Full detailed report

## 🔧 Customizing Slack Messages

See the Lambda function's `format_slack_message()` function to customize:
- Colors
- Pretext
- Number of databases shown
- Additional sections
- Interactive buttons

## 🔔 Notification Management

### Change Schedule
```bash
# Update stack with new schedule parameters
aws cloudformation update-stack \
  --stack-name rds-database-scanner \
  --use-previous-template \
  --parameters file://updated-parameters.json \
  --capabilities CAPABILITY_NAMED_IAM
```

### Change Channel
```bash
aws secretsmanager update-secret \
  --secret-id rds-scanner-slack-webhook-us-east-1 \
  --secret-string '{"webhook_url":"https://hooks.slack.com/services/...","channel":"#new-channel"}'
```

---

**Your Slack integration is ready!** 🎉
