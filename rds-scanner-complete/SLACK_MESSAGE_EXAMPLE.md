# Slack Message Preview

## What Your Team Will See Every Monday

This is an example of the automated Slack notification your team will receive every Monday at 9 AM UTC.

---

### Example Slack Message

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🔍 RDS Database Scan Results                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Scan Date: 2024-12-09 09:00 UTC
Total Databases Scanned: 47

┌────────────────────────┬────────────────────────┐
│ 🔴 Unused Databases    │ 🟡 Underused Databases │
│ 23 databases           │ 15 databases           │
├────────────────────────┼────────────────────────┤
│ 🟢 Active Databases    │ 💰 Potential Savings   │
│ 9 databases            │ ~$4,500/month          │
└────────────────────────┴────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 Unused Databases (0 transactions in 6 months)

• legacy-mysql-prod
  Engine: mysql | Instance: db.t3.medium
  Owner: john.doe@company.com | Contact: team-data@company.com
  Environment: prod

• old-analytics-db
  Engine: postgres | Instance: db.m5.large
  Owner: analytics@company.com | Contact: data-team@company.com
  Environment: stage

• staging-backup-db
  Engine: aurora-mysql | Instance: db.r5.xlarge
  Owner: devops@company.com | Contact: infrastructure@company.com
  Environment: stage

• test-db-2023
  Engine: mysql | Instance: db.t3.small
  Owner: N/A | Contact: N/A
  Environment: dev

• legacy-reporting
  Engine: postgres | Instance: db.t3.medium
  Owner: reports@company.com | Contact: bi-team@company.com
  Environment: prod

...and 18 more unused databases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟡 Underused Databases (CPU < 50% or low activity)

• reporting-db
  CPU: 12.34%; Transactions/month: 28
  Owner: reports@company.com | Contact: bi-team@company.com
  Environment: prod

• customer-analytics
  CPU: 23.45%; Transactions/month: 156
  Owner: analytics@company.com | Contact: data-team@company.com
  Environment: prod

• marketing-db
  CPU: 8.67%; Transactions/month: 12
  Owner: marketing@company.com | Contact: marketing-ops@company.com
  Environment: prod

• dev-sandbox-db
  CPU: 5.23%; Transactions/month: 3
  Owner: engineering@company.com | Contact: dev-team@company.com
  Environment: dev

• archive-db
  CPU: 15.78%; Transactions/month: 45
  Owner: data-warehouse@company.com | Contact: data-eng@company.com
  Environment: prod

...and 10 more underused databases

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Recommended Actions:
• Review and delete 23 unused database(s)
• Consider downsizing 15 underused database(s)

📊 Download Full CSV Report
   [Link: https://your-bucket.s3.amazonaws.com/rds-scans/rds_scan_20241209_090000.csv]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Message Components

### 1. **Header Section**
- Clear title with emoji icon
- Scan date and time (UTC)
- Total count of databases scanned

### 2. **Summary Dashboard**
- 🔴 **Unused**: Databases with zero transactions in 6 months
- 🟡 **Underused**: Databases with low CPU or transaction counts
- 🟢 **Active**: Properly utilized databases
- 💰 **Potential Savings**: Estimated monthly cost reduction

### 3. **Unused Databases Detail**
Shows up to 5 unused databases with:
- Database identifier
- Engine type and instance class
- Owner and contact information
- Environment (prod/stage/dev)
- Indicator of additional unused databases if more than 5

### 4. **Underused Databases Detail**
Shows up to 5 underused databases with:
- Database identifier
- Specific metrics (CPU utilization, transaction counts)
- Owner and contact information
- Environment
- Indicator of additional underused databases if more than 5

### 5. **Action Items**
- Clear, actionable recommendations
- Count of databases requiring attention
- Prioritized by impact

### 6. **Full Report Link**
- Direct download link to complete CSV report
- Stored in S3 for team access
- Contains all databases, not just top 5

---

## Why This Format Works

✅ **At-a-Glance Summary**: Team leads see key metrics immediately

✅ **Detailed Enough**: Developers see which databases need attention

✅ **Not Overwhelming**: Shows top 5 in each category, with link to full report

✅ **Actionable**: Clear next steps for the team

✅ **Automated**: No manual work required after setup

✅ **Consistent**: Same format every week builds familiarity

---

## Customization Options

### Change Number of Databases Shown

Edit `slack_notifier.py`:
```python
# Show top 10 instead of top 5
for db in unused[:10]:  # Change from [:5] to [:10]
```

### Add Team Mentions

```python
if len(unused) > 20:
    text = "<!channel> Alert: More than 20 unused databases!"
```

### Customize Cost Estimates

Edit the `_estimate_savings()` method to match your actual RDS pricing.

### Different Channels for Different Environments

```python
# Send prod issues to #cloud-ops
# Send dev issues to #engineering
if environment == 'prod':
    notifier = SlackNotifier(PROD_WEBHOOK)
else:
    notifier = SlackNotifier(DEV_WEBHOOK)
```

---

## Example Use Cases

### Weekly Cost Review
**Channel**: #finance or #cloud-costs
**Audience**: Finance team, Engineering leads
**Goal**: Track and reduce cloud spend

### Database Governance
**Channel**: #database-ops or #platform-engineering
**Audience**: DBAs, Platform engineers
**Goal**: Maintain database hygiene

### Tag Compliance
**Channel**: #cloud-governance
**Audience**: Cloud ops, Security
**Goal**: Ensure all databases have proper tags

### Development Cleanup
**Channel**: #engineering
**Audience**: All developers
**Goal**: Remove test/dev databases no longer needed

---

## Best Practices

1. **Choose the Right Channel**
   - High visibility channel for critical issues
   - Dedicated channel for automated reports
   - Consider creating #database-reports

2. **Set Expectations**
   - Pin a message explaining the automated report
   - Document who should act on findings
   - Set SLAs for database cleanup

3. **Follow Up**
   - Review trends week-over-week
   - Celebrate cost savings wins
   - Share learnings with team

4. **Iterate**
   - Adjust thresholds based on actual usage patterns
   - Customize cost estimates for accuracy
   - Add or remove metrics as needed

---

## Real-World Impact

### Example: Mid-Sized Startup (50 employees)

**Before RDS Scanner:**
- 73 RDS instances across all environments
- No visibility into usage patterns
- ~$8,500/month RDS costs
- Manual audits once per quarter

**After RDS Scanner (3 months):**
- Automated weekly Slack reports
- Deleted 28 unused databases
- Downsized 15 underused databases
- **New monthly cost: $4,200**
- **Savings: $4,300/month ($51,600/year)** 🎉

**Return on Investment:**
- Setup time: 30 minutes
- Monthly maintenance: ~5 minutes
- Monthly cost: ~$0.50
- **ROI: 8,600x** 🚀

---

**Ready to start receiving automated reports?**

Follow the [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) to get started!
