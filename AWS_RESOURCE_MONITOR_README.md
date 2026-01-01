# AWS Resource Monitor

Comprehensive weekly monitoring script that scans AWS environments for resource usage and sends Slack notifications with CSV reports uploaded to Google Drive.

## Features

- **Lambda Storage Monitoring**: Tracks storage usage, identifies unused functions and version bloat
- **IAM Role Monitoring**: Tracks IAM role count against quota
- **RDS Monitoring**: Identifies underused RDS instances (avg CPU < 10%)
- **CloudWatch Logs Monitoring**: Identifies old log groups (>90 days)
- **Multi-Environment Support**: Scans dev and staging simultaneously
- **Slack Notifications**: Formatted alerts with emoji indicators
- **CSV Reports**: Detailed reports exported to CSV
- **Google Drive Integration**: Auto-uploads reports to Google Drive

## Sample Slack Notification

```
📊 Weekly AWS Resources Usage Alert
Report Date: 2025-12-09 10:00:00
────────────────────────────────────────

DEV Environment
🟢 IAM Roles in DEV
   450 / 1000 (45.0%)

🟡 Lambda Storage in DEV
   150.5 / 300 GB (50.2%)

Bloated Lambdas: 45
Unused Lambdas: 320

Underused RDS: 2 / 15

Old CloudWatch Logs: 120 log groups (>90 days) | Total: 45.3 GB

────────────────────────────────────────

STAGE Environment
🔴 IAM Roles in STAGE
   850 / 1000 (85.0%)

🔴 Lambda Storage in STAGE
   211.1 / 300 GB (70.4%)

Bloated Lambdas: 82
Unused Lambdas: 1261

Underused RDS: 3 / 20

Old CloudWatch Logs: 245 log groups (>90 days) | Total: 67.8 GB

────────────────────────────────────────
💾 Detailed CSV report available in Google Drive
```

## Installation

### 1. Install Python Dependencies

```bash
pip3 install -r requirements-monitor.txt
```

Or install manually:

```bash
pip3 install boto3 requests google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Configure AWS Credentials

Ensure you have AWS profiles configured:

```bash
aws configure sso --profile guild-dev
aws configure sso --profile guild-stage
```

### 3. Setup Slack Webhook

1. Go to your Slack workspace
2. Create a new Incoming Webhook: https://api.slack.com/messaging/webhooks
3. Save the webhook URL

### 4. Setup Google Drive (Optional)

#### Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Drive API
4. Create Service Account:
   - IAM & Admin > Service Accounts > Create Service Account
   - Name it: `aws-resource-monitor`
   - Grant role: `Editor` (or custom role with Drive access)
5. Create Key:
   - Click on service account
   - Keys > Add Key > Create New Key
   - Choose JSON
   - Save as `google-credentials.json`

#### Share Google Drive Folder

1. Create a folder in Google Drive for reports
2. Share folder with service account email (found in JSON file)
3. Copy the folder ID from URL: `https://drive.google.com/drive/folders/FOLDER_ID_HERE`
4. Set environment variable:

```bash
export GOOGLE_DRIVE_FOLDER_ID="your-folder-id-here"
```

## Usage

### Basic Usage (with Google Drive)

```bash
python3 aws_resource_monitor.py \
  --slack-webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --google-credentials google-credentials.json \
  --dev-profile guild-dev \
  --stage-profile guild-stage \
  --region us-west-2
```

### Without Google Drive

```bash
python3 aws_resource_monitor.py \
  --slack-webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --dev-profile guild-dev \
  --stage-profile guild-stage
```

### Using Environment Variables

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
export GOOGLE_CREDENTIALS_FILE="google-credentials.json"
export GOOGLE_DRIVE_FOLDER_ID="your-folder-id"

python3 aws_resource_monitor.py \
  --slack-webhook $SLACK_WEBHOOK_URL \
  --google-credentials $GOOGLE_CREDENTIALS_FILE
```

## Command Line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--slack-webhook` | Yes | - | Slack webhook URL for notifications |
| `--google-credentials` | No | `google-credentials.json` | Path to Google service account JSON |
| `--dev-profile` | No | `guild-dev` | AWS profile for dev environment |
| `--stage-profile` | No | `guild-stage` | AWS profile for staging environment |
| `--region` | No | `us-west-2` | AWS region to scan |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_CREDENTIALS_FILE` | Path to Google service account credentials |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Drive folder ID for uploads |

## Scheduling with Cron (Weekly Automation)

Add to crontab for weekly Monday 9 AM runs:

```bash
crontab -e
```

Add this line:

```cron
0 9 * * 1 cd /path/to/RDS_Scanner && /usr/bin/python3 aws_resource_monitor.py --slack-webhook "YOUR_WEBHOOK" --google-credentials google-credentials.json >> monitor.log 2>&1
```

Or use a shell script:

```bash
#!/bin/bash
# weekly-aws-monitor.sh

cd /Users/sathyamusanipalli/git/guild/RDS_Scanner

python3 aws_resource_monitor.py \
  --slack-webhook "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  --google-credentials google-credentials.json \
  --dev-profile guild-dev \
  --stage-profile guild-stage \
  --region us-west-2
```

Make executable and add to cron:

```bash
chmod +x weekly-aws-monitor.sh
crontab -e
# Add: 0 9 * * 1 /path/to/weekly-aws-monitor.sh
```

## Output Files

### CSV Report Structure

```csv
AWS Resource Usage Report
Generated: 2025-12-09 10:00:00

=== DEV ENVIRONMENT ===

Lambda Storage
Total Functions,1450
Storage Used (GB),150.5
Storage Limit (GB),300
Storage Usage %,50.2
Unused Functions,320
Functions with Version Bloat (>10 versions),45

IAM Roles
Total Roles,450
Roles Quota,1000
Usage %,45.0

RDS Instances
Total Instances,15
Underused Instances,2
Instance Name,Avg CPU %,Engine,Instance Class
old-analytics-db,3.5,postgres,db.t3.medium
test-mysql-db,5.2,mysql,db.t3.small

CloudWatch Log Groups
Total Log Groups,850
Old Log Groups (>90 days),120
Total Storage (GB),45.3

=== STAGE ENVIRONMENT ===
...
```

## Resource Thresholds

| Resource | Warning (🟡) | Critical (🔴) |
|----------|-------------|--------------|
| Lambda Storage | >50% | >70% |
| IAM Roles | >60% | >80% |
| RDS Underused | CPU <20% | CPU <10% |
| CloudWatch Logs | >90 days old | >180 days old |
| Lambda Unused | 0 invocations (30d) | - |
| Lambda Version Bloat | >10 versions | >50 versions |

## Troubleshooting

### Issue: "No module named 'google'"

**Solution:**
```bash
pip3 install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Issue: "Google Drive credentials not found"

**Solution:**
- Ensure `google-credentials.json` exists in the script directory
- Or specify path: `--google-credentials /path/to/credentials.json`
- Or set: `export GOOGLE_CREDENTIALS_FILE=/path/to/credentials.json`

### Issue: "An error occurred (ExpiredToken)"

**Solution:**
```bash
aws sso login --profile guild-dev
aws sso login --profile guild-stage
```

### Issue: Slack notification fails with 403

**Solution:**
- Regenerate Slack webhook URL
- Ensure webhook is for correct channel
- Check webhook hasn't been revoked

### Issue: Script takes too long

**Solution:**
- This is normal for large environments (2000+ Lambdas takes 20-30 minutes)
- Run in background: `nohup python3 aws_resource_monitor.py ... &`
- Or schedule during off-hours

## Performance

- **Dev environment** (500 Lambdas, 50 RDS): ~10 minutes
- **Stage environment** (2000+ Lambdas, 100+ RDS): ~30 minutes
- **Total for both**: ~40 minutes

## Security Best Practices

1. **Never commit credentials to Git:**
   ```bash
   echo "google-credentials.json" >> .gitignore
   echo "*.log" >> .gitignore
   ```

2. **Use AWS SSO** instead of long-term credentials

3. **Restrict Google Service Account** to specific Drive folder

4. **Rotate Slack webhook** if exposed

5. **Use read-only IAM permissions** where possible

## Support

For issues or questions:
- Check CloudWatch logs for Lambda/RDS access errors
- Verify AWS profile authentication: `aws sts get-caller-identity --profile guild-dev`
- Test Slack webhook: `curl -X POST -H 'Content-type: application/json' --data '{"text":"Test"}' YOUR_WEBHOOK_URL`

## License

Internal Guild Education use only.
