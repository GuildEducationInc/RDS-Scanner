# Slack Message Examples

This document shows exactly what the Slack notifications will look like in your channel.

---

## Monday Message (With Reminder)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                            ┃
┃  ⏰ REMINDER: Weekly RDS Database Scan                     ┃
┃  Please review unused and underused databases              ┃
┃  for cost optimization!                                    ┃
┃                                                            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗄️  RDS Database Scan Results

┌────────────────────────────────────────────────────────────┐
│  Total Databases:        25                                │
│  Scan Date:              2024-12-04 09:00 UTC              │
│                                                            │
│  ❌ Unused:              5                                 │
│  ⚠️  Underused:          8                                 │
│  ✅ Active:              12                                │
│                                                            │
│  💰 Potential Savings:   ~$900/month                       │
└────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Unused Databases (Zero transactions in 6 months):
• `legacy-mysql-db` (mysql) - Owner: john@company.com
• `old-test-db` (postgres) - Owner: N/A
• `staging-backup-db` (aurora-mysql) - Owner: team-data@company.com
• `dev-temporary-db` (postgres) - Owner: sarah@company.com
• `analytics-old` (mysql) - Owner: analytics@company.com

Underused Databases (CPU < 50% OR transactions < 50/month):
• `analytics-db` - CPU: 15.23%; Transactions/month: 124 - Owner: analytics@company.com
• `reporting-db` - CPU: 32.45%; Transactions/month: 28 - Owner: reports@company.com
• `backup-replica` - CPU: 8.12%; Transactions/month: 12 - Owner: N/A
• `test-db-prod` - CPU: 45.67%; Transactions/month: 45 - Owner: test-team@company.com
• `staging-db-1` - CPU: 22.34%; Transactions/month: 35 - Owner: staging@company.com
... and 3 more underused databases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Full Report:
s3://rds-scanner-reports-123456789012/rds-scans/rds_scan_20241204_090015.csv
```

---

## Friday Message (Without Reminder)

```
🗄️  RDS Database Scan Results

┌────────────────────────────────────────────────────────────┐
│  Total Databases:        23                                │
│  Scan Date:              2024-12-06 09:00 UTC              │
│                                                            │
│  ❌ Unused:              4                                 │
│  ⚠️  Underused:          7                                 │
│  ✅ Active:              12                                │
│                                                            │
│  💰 Potential Savings:   ~$750/month                       │
└────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Unused Databases (Zero transactions in 6 months):
• `old-test-db` (postgres) - Owner: N/A
• `staging-backup-db` (aurora-mysql) - Owner: team-data@company.com
• `dev-temporary-db` (postgres) - Owner: sarah@company.com
• `analytics-old` (mysql) - Owner: analytics@company.com

Underused Databases (CPU < 50% OR transactions < 50/month):
• `analytics-db` - CPU: 15.23%; Transactions/month: 124 - Owner: analytics@company.com
• `reporting-db` - CPU: 32.45%; Transactions/month: 28 - Owner: reports@company.com
• `backup-replica` - CPU: 8.12%; Transactions/month: 12 - Owner: N/A
• `test-db-prod` - CPU: 45.67%; Transactions/month: 45 - Owner: test-team@company.com
• `staging-db-1` - CPU: 22.34%; Transactions/month: 35 - Owner: staging@company.com
... and 2 more underused databases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Full Report:
s3://rds-scanner-reports-123456789012/rds-scans/rds_scan_20241206_090015.csv
```

---

## Message Features

### Key Differences

| Feature | Monday | Friday |
|---------|--------|--------|
| **Reminder Pretext** | ✅ Yes | ❌ No |
| **Report** | ✅ Full scan | ✅ Full scan |
| **Time** | 9:00 AM UTC | 9:00 AM UTC |
| **Purpose** | Weekly review reminder | Status update |

### What's Included

✅ **Summary Stats**
- Total database count
- Unused count (0 transactions in 6 months)
- Underused count (CPU < 50% OR transactions < 50/month)
- Active database count
- Estimated monthly savings

✅ **Unused Databases**
- Database identifier
- Engine type (postgres, mysql, etc.)
- Owner from tags

✅ **Underused Databases**
- Database identifier
- Specific metrics (CPU %, transaction count)
- Owner from tags

✅ **S3 Report Link**
- Direct link to detailed CSV report

### Emoji Guide

| Emoji | Meaning |
|-------|---------|
| ⏰ | Monday reminder |
| 🗄️ | Database scan results |
| ❌ | Unused database |
| ⚠️ | Underused database |
| ✅ | Active database |
| 💰 | Potential cost savings |
| 📊 | Full report link |

---

## Sample Slack Channel Setup

### Recommended Channel: `#database-ops` or `#cloud-costs`

**Channel Description:**
```
RDS database monitoring and cost optimization alerts.
Receives automated scans every Monday (with reminders) and Friday.
```

**Pinned Message:**
```
📌 RDS Scanner Information

This channel receives automated RDS database scans:
• Monday 9:00 AM UTC - With reminder to review
• Friday 9:00 AM UTC - Weekly status update

Action Items:
1. Review unused databases → Consider deletion
2. Review underused databases → Consider downsizing
3. Tag databases without owners
4. Download CSV reports from S3 for detailed analysis

Questions? Contact: cloud-ops@company.com
```

---

## How to Customize Messages

### Change Threshold Values

Edit the CloudFormation parameters:

```json
{
  "ParameterKey": "CPUThreshold",
  "ParameterValue": "40"  // Change from 50 to 40
},
{
  "ParameterKey": "TransactionThreshold",
  "ParameterValue": "100"  // Change from 50 to 100
}
```

### Modify Message Format

Edit the Lambda code in the CloudFormation template:

Look for the `format_slack_message` function and customize:
- Add more emojis
- Change text formatting
- Add action buttons
- Include additional metrics

### Add Mentions

To mention specific users or groups:

```python
pretext = "⏰ *REMINDER* <@USER_ID>: Weekly RDS Database Scan"
# or
pretext = "⏰ *REMINDER* <!channel>: Weekly RDS Database Scan"
```

### Add Action Buttons

```python
blocks.append({
    "type": "actions",
    "elements": [
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "View Report"},
            "url": f"https://s3.console.aws.amazon.com/..."
        }
    ]
})
```

---

## Testing Messages

### Test Monday Message
```bash
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": true}' \
  response.json
```

### Test Friday Message
```bash
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": false}' \
  response.json
```

---

## Troubleshooting Slack Messages

### Message Not Appearing

1. **Verify webhook URL:**
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  YOUR_WEBHOOK_URL
```

2. **Check Lambda logs:**
```bash
aws logs tail /aws/lambda/rds-scanner-function --follow
```

3. **Verify Lambda environment variables:**
```bash
aws lambda get-function-configuration \
  --function-name rds-scanner-function \
  --query 'Environment.Variables'
```

### Message Format Issues

- Ensure webhook URL is correct
- Check that channel still exists
- Verify bot permissions in Slack

### No Databases Listed

- Ensure databases have tags
- Check that regions are correct
- Verify CloudWatch metrics are available

---

## Best Practices

1. **Create Dedicated Channel**: Use `#database-ops` or similar
2. **Pin Important Info**: Pin a message with action items
3. **Set Notifications**: Configure channel notifications appropriately
4. **Regular Review**: Assign team members to review weekly
5. **Track Actions**: Use Slack threads to discuss specific databases
6. **Document Decisions**: Keep a record of what was actioned

---

## Example Team Workflow

### Monday Morning (9:00 AM)
- ⏰ Reminder message arrives
- Team reviews unused databases
- Decision: Which to delete?
- Tag databases without owners

### Throughout the Week
- DBA team reviews underused databases
- Plan downsizing for next maintenance window
- Update database tags

### Friday Morning (9:00 AM)
- Status update arrives
- Verify Monday actions were taken
- Plan for next week

### Result
- 💰 Cost savings realized
- 📊 Better database governance
- ✅ Improved resource utilization

---

**Ready to deploy?** Run `./deploy.sh` to get started! 🚀
