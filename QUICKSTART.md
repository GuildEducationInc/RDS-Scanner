# Quick Start Guide - AWS Resource Monitor

Get up and running in 5 minutes!

## Step 1: Install Dependencies (1 minute)

```bash
cd /Users/sathyamusanipalli/git/guild/RDS_Scanner
pip3 install -r requirements-monitor.txt
```

## Step 2: Configure Slack Webhook (1 minute)

1. Get your Slack webhook URL:
   - Go to: https://api.slack.com/messaging/webhooks
   - Or ask your Slack admin for the webhook URL

2. Edit `run-weekly-monitor.sh`:
   ```bash
   nano run-weekly-monitor.sh
   ```

3. Replace this line:
   ```bash
   SLACK_WEBHOOK="YOUR_SLACK_WEBHOOK_URL_HERE"
   ```

   With your actual webhook:
   ```bash
   SLACK_WEBHOOK="https://hooks.slack.com/services/T0G6T8SLC/B0A24337UAX/YourActualWebhookURL"
   ```

## Step 3: Test Run (2 minutes)

### Option A: Quick test without Google Drive

```bash
./run-weekly-monitor.sh
```

The script will:
- ✓ Check dependencies
- ✓ Authenticate with AWS (will prompt for SSO if needed)
- ✓ Scan both dev and stage environments
- ✓ Send Slack notification
- ✗ Skip Google Drive upload (credentials not configured)

### Option B: Full test with Google Drive

If you want to upload reports to Google Drive:

1. Get Google service account credentials (see AWS_RESOURCE_MONITOR_README.md)
2. Save as `google-credentials.json`
3. Run the script:
   ```bash
   ./run-weekly-monitor.sh
   ```

## Step 4: Schedule Weekly Runs (1 minute)

Add to crontab for automatic weekly runs (Mondays at 9 AM):

```bash
crontab -e
```

Add this line:

```cron
0 9 * * 1 cd /Users/sathyamusanipalli/git/guild/RDS_Scanner && ./run-weekly-monitor.sh >> monitor.log 2>&1
```

Save and exit (`:wq` in vim or Ctrl+X in nano).

## That's it! 🎉

You'll now receive weekly Slack alerts like this:

```
📊 Weekly AWS Resources Usage Alert

DEV Environment
🟢 IAM Roles in DEV: 450 / 1000 (45.0%)
🟡 Lambda Storage in DEV: 150.5 / 300 GB (50.2%)
Bloated Lambdas: 45 | Unused Lambdas: 320
Underused RDS: 2 / 15

STAGE Environment
🔴 IAM Roles in STAGE: 850 / 1000 (85.0%)
🔴 Lambda Storage in STAGE: 211.1 / 300 GB (70.4%)
Bloated Lambdas: 82 | Unused Lambdas: 1261
Underused RDS: 3 / 20

💾 Detailed CSV report available
```

## Manual Run Anytime

```bash
# Full command with all options
python3 aws_resource_monitor.py \
  --slack-webhook "YOUR_WEBHOOK_URL" \
  --dev-profile guild-dev \
  --stage-profile guild-stage \
  --region us-west-2

# Or use the shell script
./run-weekly-monitor.sh
```

## Troubleshooting

### "AWS profile expired"

```bash
aws sso login --profile guild-dev
aws sso login --profile guild-stage
```

### "Slack notification failed"

- Check your webhook URL is correct
- Test it manually:
  ```bash
  curl -X POST -H 'Content-type: application/json' \
    --data '{"text":"Test message"}' \
    YOUR_WEBHOOK_URL
  ```

### "Script takes too long"

- This is normal! 2000+ Lambdas takes 30-40 minutes
- Run in background:
  ```bash
  nohup ./run-weekly-monitor.sh > monitor.log 2>&1 &
  tail -f monitor.log  # Watch progress
  ```

## What Gets Scanned?

✅ **Lambda Functions**
- Storage usage vs 300GB limit
- Unused functions (0 invocations in 30 days)
- Version bloat (>10 versions)

✅ **IAM Roles**
- Total count vs quota (1000)
- Usage percentage

✅ **RDS Instances**
- Underused databases (avg CPU <10% over 7 days)
- Instance details (engine, size, CPU)

✅ **CloudWatch Logs**
- Old log groups (>90 days)
- Total storage consumed

## Next Steps

- Read full documentation: [AWS_RESOURCE_MONITOR_README.md](AWS_RESOURCE_MONITOR_README.md)
- Setup Google Drive integration for report storage
- Customize Slack notification format
- Add more environments (prod, etc.)

## Need Help?

Check the full README: `AWS_RESOURCE_MONITOR_README.md`
