# RDS Scanner - Automated Database Cost Optimization

[![Deploy to AWS](https://github.com/YOUR_USERNAME/rds-scanner/actions/workflows/deploy.yml/badge.svg)](https://github.com/YOUR_USERNAME/rds-scanner/actions/workflows/deploy.yml)
[![Test Scanner](https://github.com/YOUR_USERNAME/rds-scanner/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/rds-scanner/actions/workflows/test.yml)

Automated AWS RDS database scanner that identifies unused and underused databases, with scheduled Slack notifications and CI/CD via GitHub Actions.

## 🎯 Features

- 🔍 **Automated Scanning** - Identifies unused and underused RDS databases
- 📅 **Scheduled Runs** - Every Monday (with reminder) and Friday at 9 AM UTC
- 💬 **Slack Integration** - Beautiful formatted notifications
- 💾 **S3 Reports** - Detailed CSV reports with 90-day retention
- 💰 **Cost Insights** - Estimates potential monthly savings
- 🏷️ **Tag Tracking** - Extracts owner, contact, and repo tags
- 🚀 **GitHub Actions** - Automated deployment and testing
- 📊 **CloudFormation** - Infrastructure as Code

## 🚀 Quick Start

### 1. Configure Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description | Get It From |
|--------|-------------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS access key | AWS IAM Console |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | AWS IAM Console |
| `SLACK_WEBHOOK_URL` | Slack webhook | https://api.slack.com/messaging/webhooks |

### 2. Deploy

Push to `main` branch or manually trigger via **Actions** tab.

```bash
git push origin main
```

### 3. Test

Go to **Actions → Test RDS Scanner → Run workflow**

---

## 📁 Repository Structure

```
rds-scanner/
├── .github/
│   └── workflows/
│       ├── deploy.yml         # Automated deployment
│       ├── test.yml           # Manual testing
│       ├── destroy.yml        # Safe stack deletion
│       └── pr-validation.yml  # PR checks
├── rds-scanner-cloudformation.yaml  # Infrastructure template
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── GITHUB_DEPLOYMENT.md       # Full deployment guide
├── GITHUB_QUICKSTART.md       # 10-minute setup
└── SLACK_MESSAGE_EXAMPLES.md  # Notification examples
```

---

## 🤖 GitHub Actions Workflows

### Deploy Workflow
**File:** `.github/workflows/deploy.yml`

**Triggers:**
- Push to `main` or `production` branch
- Manual trigger via Actions tab

**Steps:**
1. Validates CloudFormation template
2. Deploys/updates stack
3. Tests Lambda function
4. Notifies Slack

**View:** [Actions → Deploy RDS Scanner to AWS](../../actions/workflows/deploy.yml)

### Test Workflow
**File:** `.github/workflows/test.yml`

**Triggers:**
- Manual only (via Actions tab)

**Options:**
- Test with Monday reminder
- Test with Friday (no reminder)

**View:** [Actions → Test RDS Scanner](../../actions/workflows/test.yml)

### Destroy Workflow
**File:** `.github/workflows/destroy.yml`

**Triggers:**
- Manual only (safety measure)

**Requires:**
- Type "DELETE" to confirm
- Option to empty S3 bucket

**View:** [Actions → Destroy RDS Scanner Stack](../../actions/workflows/destroy.yml)

### PR Validation
**File:** `.github/workflows/pr-validation.yml`

**Triggers:**
- Pull requests to `main`

**Checks:**
- CloudFormation validation
- Secret scanning
- Template linting

**View:** [Pull Requests](../../pulls)

---

## 💬 Slack Notifications

### Monday Message (9:00 AM UTC)
```
⏰ REMINDER: Weekly RDS Database Scan
Please review unused and underused databases for cost optimization!

🗄️ RDS Database Scan Results
Total Databases: 25
❌ Unused: 5
⚠️ Underused: 8
✅ Active: 12
💰 Potential Savings: ~$900/month
```

### Friday Message (9:00 AM UTC)
Same format without the reminder pretext.

[See full examples →](SLACK_MESSAGE_EXAMPLES.md)

---

## 📊 What Gets Scanned

### Database Categories

**🔴 Unused (Action: Delete or Archive)**
- Zero transactions in last 6 months
- Estimated savings: ~$100/db/month

**🟡 Underused (Action: Downsize)**
- CPU < 50% (6-month average) OR
- Transactions < 50 per month
- Estimated savings: ~$50/db/month

**🟢 Active**
- Normal usage
- No action needed

---

## 🎛️ Configuration

### Scan Regions

**Option 1:** GitHub Secret
```
Name: SCAN_REGIONS
Value: us-east-1,us-west-2,eu-west-1
```

**Option 2:** Edit workflow default

### Thresholds

Edit `rds-scanner-cloudformation.yaml`:
```yaml
CPUThreshold:
  Default: 50

TransactionThreshold:
  Default: 50
```

### Schedule

Edit `rds-scanner-cloudformation.yaml`:
```yaml
MondayScheduleRule:
  ScheduleExpression: 'cron(0 9 ? * MON *)'

FridayScheduleRule:
  ScheduleExpression: 'cron(0 9 ? * FRI *)'
```

---

## 🔄 Development Workflow

### Make Changes

```bash
# 1. Create feature branch
git checkout -b feature/update-threshold

# 2. Make changes
vim rds-scanner-cloudformation.yaml

# 3. Commit
git commit -am "Update CPU threshold"

# 4. Push
git push origin feature/update-threshold

# 5. Create PR
# PR validation runs automatically
```

### Deploy Changes

```bash
# Merge PR via GitHub UI
# Deploy workflow runs automatically on merge
```

---

## 📋 Deployed Resources

| Resource | Description | Cost |
|----------|-------------|------|
| **Lambda Function** | Scans RDS databases | ~$0.50/month |
| **S3 Bucket** | Stores CSV reports | ~$0.10/month |
| **EventBridge Rules** | Monday & Friday schedules | Free |
| **IAM Role** | Lambda execution role | Free |
| **CloudWatch Logs** | Lambda logs (30-day retention) | ~$0.50/month |
| **Total** | | **~$1-2/month** |

### Potential Savings
- Small team: $300-$500/month
- Medium company: $1,000-$2,000/month
- Enterprise: $5,000-$10,000+/month

**ROI: 500-10,000x** 🎯

---

## 🛠️ Troubleshooting

### Deployment Fails
1. Check **Actions** tab for error logs
2. Verify GitHub Secrets are correct
3. Check IAM permissions in AWS

### No Slack Notifications
1. Verify `SLACK_WEBHOOK_URL` secret
2. Check Lambda logs in CloudWatch
3. Test webhook manually:
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test"}'
```

### Lambda Timeout
- Increase timeout in CloudFormation template
- Default: 900 seconds (15 minutes)

### No Databases Found
- Verify `SCAN_REGIONS` includes correct regions
- Check AWS credentials have RDS read permissions

---

## 📚 Documentation

- **[GITHUB_QUICKSTART.md](GITHUB_QUICKSTART.md)** - 10-minute setup guide
- **[GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)** - Complete deployment guide
- **[SLACK_MESSAGE_EXAMPLES.md](SLACK_MESSAGE_EXAMPLES.md)** - Notification examples
- **[README_CLOUDFORMATION.md](README_CLOUDFORMATION.md)** - CloudFormation details

---

## 🔒 Security

### GitHub Secrets
- Never commit credentials
- Use repository secrets for sensitive data
- Consider GitHub Environments for production

### IAM Permissions
- Use least privilege IAM policies
- Consider OIDC instead of access keys
- Rotate credentials regularly

### Branch Protection
Enable on `main` branch:
- Require PR reviews
- Require status checks
- Prevent force pushes

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -am 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

PR validation will automatically run!

---

## 📊 Monitoring

### GitHub Actions
- View workflow runs in **Actions** tab
- Download test artifacts
- Review deployment logs

### AWS CloudWatch
```bash
# Follow Lambda logs
aws logs tail /aws/lambda/rds-scanner-function --follow
```

### S3 Reports
```bash
# List all reports
aws s3 ls s3://rds-scanner-reports-ACCOUNT-ID/rds-scans/

# Download latest
aws s3 cp s3://rds-scanner-reports-ACCOUNT-ID/rds-scans/ ./ --recursive
```

---

## 🎯 Next Steps

1. ✅ Configure GitHub Secrets
2. ✅ Push to main to deploy
3. ✅ Test via Actions tab
4. ✅ Wait for Monday scheduled run
5. ✅ Review Slack notification
6. ✅ Download S3 report
7. ✅ Take action on unused databases
8. ✅ Track cost savings!

---

## 📞 Support

- **Issues:** [Create an issue](../../issues)
- **Discussions:** [Start a discussion](../../discussions)
- **Actions Logs:** [View workflow runs](../../actions)

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- AWS CloudFormation for IaC
- GitHub Actions for CI/CD
- Slack for notifications

---

**Start saving money today!** 🚀

Push to main and let GitHub Actions handle the deployment.

**Questions?** Check [GITHUB_QUICKSTART.md](GITHUB_QUICKSTART.md) or [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)
