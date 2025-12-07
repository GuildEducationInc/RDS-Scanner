# GitHub Deployment - Quick Start

Deploy RDS Scanner to AWS using GitHub Actions in 10 minutes!

## ⚡ Super Quick Setup

### 1. Create GitHub Repository

```bash
# On GitHub, click "New Repository"
# Name it: rds-scanner
# Initialize with README: No
# Clone it locally:
git clone https://github.com/YOUR_USERNAME/rds-scanner.git
cd rds-scanner
```

### 2. Add Files

Copy all files from this package to your repository:

```bash
# Required files:
- rds-scanner-cloudformation.yaml
- .github/workflows/deploy.yml
- .github/workflows/test.yml
- .github/workflows/destroy.yml
- .github/workflows/pr-validation.yml
- .gitignore
- README.md
- GITHUB_DEPLOYMENT.md

# Add all files
git add .
git commit -m "Initial commit: RDS Scanner"
git push origin main
```

### 3. Configure GitHub Secrets

Go to: **Your Repo → Settings → Secrets and variables → Actions**

Click **"New repository secret"** and add these 3 secrets:

#### Secret 1: AWS_ACCESS_KEY_ID
```
Name: AWS_ACCESS_KEY_ID
Value: AKIAIOSFODNN7EXAMPLE
```

#### Secret 2: AWS_SECRET_ACCESS_KEY
```
Name: AWS_SECRET_ACCESS_KEY
Value: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

#### Secret 3: SLACK_WEBHOOK_URL
```
Name: SLACK_WEBHOOK_URL
Value: https://hooks.slack.com/services/XXX/YYY/ZZZ
```

**Get Slack Webhook:**
1. Visit: https://api.slack.com/messaging/webhooks
2. Create webhook → Select channel
3. Copy URL

### 4. Deploy!

```bash
# Push to main branch to trigger deployment
git push origin main

# Or manually trigger via GitHub Actions:
# 1. Go to "Actions" tab
# 2. Click "Deploy RDS Scanner to AWS"
# 3. Click "Run workflow"
# 4. Click green "Run workflow" button
```

### 5. Watch It Deploy

1. Go to **Actions** tab in GitHub
2. Watch deployment progress
3. See CloudFormation stack creation
4. View test results
5. Check Slack for notification!

---

## 🎯 What Happens

When you push to `main` branch, GitHub Actions automatically:

1. ✅ Validates CloudFormation template
2. ✅ Creates/Updates CloudFormation stack in AWS
3. ✅ Deploys Lambda function
4. ✅ Creates S3 bucket for reports
5. ✅ Sets up EventBridge schedules (Mon & Fri)
6. ✅ Tests Lambda function
7. ✅ Sends notification to Slack

**Total time:** 3-4 minutes

---

## 📱 Test It

### Manual Test via GitHub Actions

1. Go to **Actions** tab
2. Click **"Test RDS Scanner"**
3. Click **"Run workflow"**
4. Select:
   - ✅ **is_monday: true** (for Monday reminder test)
   - or
   - ❌ **is_monday: false** (for Friday test)
5. Click **"Run workflow"**
6. Check Slack for test message!

### Manual Test via AWS CLI

```bash
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": true}' \
  response.json

cat response.json
```

---

## 🔍 View Results

### GitHub Actions Logs
- **Actions** tab → Click workflow run → View logs

### AWS CloudFormation Stack
```bash
aws cloudformation describe-stacks --stack-name rds-scanner
```

### Lambda Logs
```bash
aws logs tail /aws/lambda/rds-scanner-function --follow
```

### S3 Reports
```bash
aws s3 ls s3://rds-scanner-reports-YOUR-ACCOUNT-ID/rds-scans/
```

### Slack Channel
- Check your configured Slack channel
- You should see deployment notification
- Scheduled scans will appear Mon & Fri at 9 AM UTC

---

## 🎛️ Customize

### Change Scan Regions

**Option 1: Add GitHub Secret**
1. Go to **Settings → Secrets → Actions**
2. Add secret: `SCAN_REGIONS`
3. Value: `us-east-1,us-west-2,eu-west-1`
4. Redeploy (push any commit)

**Option 2: Edit Workflow**
1. Edit `.github/workflows/deploy.yml`
2. Find `"ParameterValue": "${{ secrets.SCAN_REGIONS || 'us-east-1,us-west-2' }}"`
3. Change default value
4. Commit and push

### Change Thresholds

Edit `rds-scanner-cloudformation.yaml`:

```yaml
CPUThreshold:
  Default: 40  # Changed from 50

TransactionThreshold:
  Default: 100  # Changed from 50
```

Commit and push to deploy.

### Change Schedule

Edit `rds-scanner-cloudformation.yaml`:

```yaml
# Run every day at 8 AM UTC instead
MondayScheduleRule:
  ScheduleExpression: 'cron(0 8 * * ? *)'
```

---

## 🔄 Update Process

### Make Changes

```bash
# 1. Create feature branch
git checkout -b feature/update-threshold

# 2. Edit CloudFormation template
vim rds-scanner-cloudformation.yaml

# 3. Commit changes
git add rds-scanner-cloudformation.yaml
git commit -m "Update CPU threshold to 40%"

# 4. Push branch
git push origin feature/update-threshold
```

### Create Pull Request

1. Go to GitHub repository
2. Click **"Pull requests"**
3. Click **"New pull request"**
4. Select your feature branch
5. Click **"Create pull request"**

**PR Validation runs automatically!**
- ✅ Validates CloudFormation
- ✅ Checks for secrets
- ✅ Lints template
- ✅ Comments results on PR

### Merge to Deploy

1. Review PR validation results
2. Click **"Merge pull request"**
3. **Deploy workflow runs automatically!**
4. Check **Actions** tab for deployment status

---

## 🗑️ Delete Stack

### Via GitHub Actions (Safe Method)

1. Go to **Actions** tab
2. Click **"Destroy RDS Scanner Stack"**
3. Click **"Run workflow"**
4. Type `DELETE` in confirmation
5. Check "Empty S3 bucket"
6. Click **"Run workflow"**

### Via AWS CLI

```bash
# Empty S3 bucket first
aws s3 rm s3://rds-scanner-reports-YOUR-ACCOUNT-ID --recursive

# Delete stack
aws cloudformation delete-stack --stack-name rds-scanner
```

---

## 🛠️ Troubleshooting

### Deployment Fails

**Check GitHub Actions logs:**
1. **Actions** tab → Failed workflow → View logs
2. Look for error messages in "Deploy CloudFormation Stack" step

**Common issues:**
- ❌ Invalid AWS credentials → Verify GitHub Secrets
- ❌ Stack already exists → Workflow handles updates automatically
- ❌ Permission denied → Check IAM policy
- ❌ Template validation error → Check CloudFormation syntax

### Secrets Not Working

**Verify secret names exactly match:**
- `AWS_ACCESS_KEY_ID` ✅ (not AWS_ACCESS_KEY)
- `AWS_SECRET_ACCESS_KEY` ✅ (not AWS_SECRET_KEY)
- `SLACK_WEBHOOK_URL` ✅ (not SLACK_WEBHOOK)

**Secrets are case-sensitive!**

### No Slack Notifications

1. **Test webhook manually:**
```bash
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test from command line"}'
```

2. **Check Lambda logs:**
```bash
aws logs tail /aws/lambda/rds-scanner-function --follow
```

3. **Verify secret value:**
   - Go to **Settings → Secrets → Actions**
   - Edit `SLACK_WEBHOOK_URL`
   - Make sure it starts with `https://hooks.slack.com/services/`

---

## 📋 Checklist

Setup:
- [ ] Repository created on GitHub
- [ ] Files copied and committed
- [ ] AWS credentials added to GitHub Secrets
- [ ] Slack webhook added to GitHub Secrets
- [ ] Pushed to main branch

Deployment:
- [ ] GitHub Actions workflow ran
- [ ] CloudFormation stack created
- [ ] Lambda function deployed
- [ ] S3 bucket created
- [ ] EventBridge rules configured

Testing:
- [ ] Manual test workflow run
- [ ] Slack notification received
- [ ] S3 report generated
- [ ] Lambda logs visible in CloudWatch

Scheduled Runs:
- [ ] Monday 9 AM UTC scheduled ✅
- [ ] Friday 9 AM UTC scheduled ✅
- [ ] First Monday run successful
- [ ] First Friday run successful

---

## 🎯 What's Next?

1. ✅ Wait for Monday 9 AM UTC
2. ✅ Check Slack for first automated scan (with reminder)
3. ✅ Review S3 report
4. ✅ Take action on unused/underused databases
5. ✅ Track cost savings!

---

## 📚 More Information

- **Full Guide:** [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)
- **CloudFormation Details:** [README_CLOUDFORMATION.md](README_CLOUDFORMATION.md)
- **Slack Examples:** [SLACK_MESSAGE_EXAMPLES.md](SLACK_MESSAGE_EXAMPLES.md)

---

## 💡 Tips

### Use Branch Protection

1. **Settings → Branches**
2. Click **"Add rule"**
3. Branch name: `main`
4. Enable:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass
5. Save

### Enable Dependabot

GitHub can automatically update dependencies:
1. **Settings → Code security and analysis**
2. Enable **Dependabot alerts**
3. Enable **Dependabot security updates**

### Monitor Costs

Check AWS billing:
```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-12-01,End=2024-12-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --group-by Type=SERVICE
```

---

## 🎉 Success!

You now have:
- ✅ Automated RDS scanning
- ✅ Slack notifications twice weekly
- ✅ CI/CD pipeline via GitHub Actions
- ✅ Infrastructure as Code
- ✅ Version controlled configuration

**Cost:** ~$1-2/month AWS + Free GitHub Actions  
**Savings:** $500-$10,000+/month (by optimizing databases)  
**ROI:** 500-10,000x 🎯

---

**Need help?**  
Check [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) for detailed documentation.

**Ready to deploy?**  
Push to main! 🚀
