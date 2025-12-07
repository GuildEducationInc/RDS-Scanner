# 🎯 GitHub Deployment Package - Complete Guide

## 📦 What You Have

A complete GitHub Actions CI/CD solution for deploying RDS Scanner to AWS with automated Slack notifications.

---

## ⚡ Super Quick Start (3 Steps)

### Step 1: Create GitHub Repository
```bash
# Create new repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/rds-scanner.git
cd rds-scanner
```

### Step 2: Copy All These Files
```
Copy entire contents to your repository:
- rds-scanner-cloudformation.yaml
- .github/workflows/ (all 4 workflow files)
- .gitignore
- README_GITHUB.md (rename to README.md)
- All documentation files
```

### Step 3: Configure & Deploy
```bash
# 1. Add GitHub Secrets (Settings → Secrets → Actions):
#    - AWS_ACCESS_KEY_ID
#    - AWS_SECRET_ACCESS_KEY
#    - SLACK_WEBHOOK_URL

# 2. Commit and push
git add .
git commit -m "Initial commit"
git push origin main

# 3. Done! GitHub Actions deploys automatically
```

---

## 📁 Complete File Structure

### Repository Layout
```
rds-scanner/                           # Your GitHub repository
├── .github/
│   └── workflows/
│       ├── deploy.yml                 # ⭐ Main deployment
│       ├── test.yml                   # 🧪 Manual testing
│       ├── destroy.yml                # 🗑️ Stack deletion
│       └── pr-validation.yml          # ✅ PR checks
├── .gitignore                         # 🚫 Ignore rules
├── rds-scanner-cloudformation.yaml    # 📋 Infrastructure
├── README.md                          # 📖 Main docs (use README_GITHUB.md)
├── GITHUB_QUICKSTART.md              # ⚡ 10-min setup
├── GITHUB_DEPLOYMENT.md              # 📚 Full guide
└── SLACK_MESSAGE_EXAMPLES.md         # 💬 Slack previews
```

---

## 🤖 GitHub Actions Workflows

### 1. Deploy Workflow (`.github/workflows/deploy.yml`)

**What it does:**
- ✅ Validates CloudFormation template
- ✅ Creates/updates AWS stack
- ✅ Deploys Lambda, S3, EventBridge
- ✅ Tests Lambda function
- ✅ Sends Slack notification

**When it runs:**
- Push to `main` or `production` branch
- Manual trigger via Actions tab

**Environment:**
- Uses GitHub Secrets for credentials
- Creates parameters.json automatically
- Deploys to AWS region specified

**Example trigger:**
```bash
git push origin main  # Automatically deploys
```

---

### 2. Test Workflow (`.github/workflows/test.yml`)

**What it does:**
- ✅ Invokes Lambda function manually
- ✅ Displays response and logs
- ✅ Uploads artifacts
- ✅ Notifies Slack of results

**When it runs:**
- Manual only (safety measure)

**How to use:**
1. Go to **Actions** tab
2. Click "Test RDS Scanner"
3. Click "Run workflow"
4. Choose: Monday (with reminder) or Friday
5. Click "Run workflow"

---

### 3. Destroy Workflow (`.github/workflows/destroy.yml`)

**What it does:**
- ✅ Validates deletion confirmation
- ✅ Empties S3 bucket
- ✅ Deletes CloudFormation stack
- ✅ Notifies Slack

**When it runs:**
- Manual only (requires typing "DELETE")

**How to use:**
1. Go to **Actions** tab
2. Click "Destroy RDS Scanner Stack"
3. Click "Run workflow"
4. Type `DELETE` in confirmation
5. Check "Empty S3 bucket"
6. Click "Run workflow"

⚠️ **This permanently deletes all resources!**

---

### 4. PR Validation (`.github/workflows/pr-validation.yml`)

**What it does:**
- ✅ Validates CloudFormation template
- ✅ Scans for hardcoded secrets
- ✅ Lints CloudFormation
- ✅ Comments results on PR

**When it runs:**
- Automatically on pull requests to `main`

**What it checks:**
- Template syntax
- Parameter definitions
- No credentials in code
- CloudFormation best practices

---

## 🔑 Required GitHub Secrets

### Setting Up Secrets

**Location:** Your Repo → Settings → Secrets and variables → Actions

Click **"New repository secret"** for each:

### 1. AWS_ACCESS_KEY_ID
```
Name: AWS_ACCESS_KEY_ID
Value: AKIAIOSFODNN7EXAMPLE
```

**How to get:**
1. AWS Console → IAM → Users
2. Create user or select existing
3. Attach policies (see below)
4. Create access key
5. Copy Access Key ID

### 2. AWS_SECRET_ACCESS_KEY
```
Name: AWS_SECRET_ACCESS_KEY
Value: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**How to get:**
- Same as above
- Copy Secret Access Key (shown only once!)

### 3. SLACK_WEBHOOK_URL
```
Name: SLACK_WEBHOOK_URL
Value: https://hooks.slack.com/services/T00/B00/XXXX
```

**How to get:**
1. Visit: https://api.slack.com/messaging/webhooks
2. Create your Slack app
3. Enable Incoming Webhooks
4. Add to workspace
5. Select channel (#database-ops)
6. Copy webhook URL

### 4. SCAN_REGIONS (Optional)
```
Name: SCAN_REGIONS
Value: us-east-1,us-west-2,eu-west-1
```

**Default if not set:** `us-east-1,us-west-2`

---

## 🔐 Required IAM Permissions

Your AWS IAM user needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "lambda:*",
        "iam:*",
        "s3:*",
        "logs:*",
        "events:*",
        "rds:Describe*",
        "rds:ListTagsForResource",
        "cloudwatch:GetMetricStatistics"
      ],
      "Resource": "*"
    }
  ]
}
```

**Apply this policy to your IAM user in AWS Console**

---

## 🎬 Usage Examples

### Example 1: Initial Deployment

```bash
# 1. Clone your GitHub repository
git clone https://github.com/YOUR_USERNAME/rds-scanner.git
cd rds-scanner

# 2. Copy all files from this package

# 3. Configure GitHub Secrets (via web UI)

# 4. Commit and push
git add .
git commit -m "Initial deployment"
git push origin main

# 5. Watch deployment in Actions tab
```

**Result:** Stack deploys automatically in 3-4 minutes

---

### Example 2: Update Configuration

```bash
# 1. Create feature branch
git checkout -b update/cpu-threshold

# 2. Edit CloudFormation template
vim rds-scanner-cloudformation.yaml
# Change CPUThreshold default from 50 to 40

# 3. Commit and push
git add rds-scanner-cloudformation.yaml
git commit -m "Lower CPU threshold to 40%"
git push origin update/cpu-threshold

# 4. Create PR on GitHub
# PR validation runs automatically

# 5. Merge PR
# Deploy workflow runs automatically
```

---

### Example 3: Manual Test

1. Go to **Actions** tab in GitHub
2. Click **"Test RDS Scanner"**
3. Click **"Run workflow"**
4. Select: ✅ **is_monday: true**
5. Click **"Run workflow"**
6. Wait 2-3 minutes
7. Check Slack for test message with Monday reminder

---

### Example 4: View Reports

```bash
# List all reports in S3
aws s3 ls s3://rds-scanner-reports-ACCOUNT-ID/rds-scans/

# Download latest report
aws s3 cp s3://rds-scanner-reports-ACCOUNT-ID/rds-scans/ ./ \
  --recursive --exclude "*" --include "rds_scan_*.csv"

# View in Excel or CSV viewer
```

---

## 📊 What Gets Deployed

### AWS Resources Created

| Resource | Name | Description |
|----------|------|-------------|
| **Lambda Function** | rds-scanner-function | Scans RDS databases |
| **S3 Bucket** | rds-scanner-reports-{ACCOUNT} | Stores CSV reports |
| **IAM Role** | rds-scanner-lambda-role | Lambda execution role |
| **EventBridge Rule** | rds-scanner-monday-schedule | Monday 9 AM UTC trigger |
| **EventBridge Rule** | rds-scanner-friday-schedule | Friday 9 AM UTC trigger |
| **CloudWatch Log Group** | /aws/lambda/rds-scanner-function | Lambda logs |

**Total Cost:** ~$1-2/month

---

## 💬 Slack Notifications

### Deployment Notification
```
✅ RDS Scanner Deployment
Deployment Status: Success

Repository: your-org/rds-scanner
Branch: main
Commit: abc123
Actor: your-username
```

### Monday Scan (9:00 AM UTC)
```
⏰ REMINDER: Weekly RDS Database Scan
Please review unused and underused databases for cost optimization!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗄️ RDS Database Scan Results

Total Databases: 25
❌ Unused: 5
⚠️ Underused: 8
✅ Active: 12
💰 Potential Savings: ~$900/month

[Lists databases with details...]

📊 Full Report: s3://bucket/report.csv
```

### Friday Scan (9:00 AM UTC)
Same format without reminder pretext.

---

## 🔄 Development Workflow

### Step-by-Step Process

1. **Create Feature Branch**
```bash
git checkout -b feature/new-feature
```

2. **Make Changes**
```bash
vim rds-scanner-cloudformation.yaml
# or
vim .github/workflows/deploy.yml
```

3. **Commit Changes**
```bash
git add .
git commit -m "Description of changes"
```

4. **Push Branch**
```bash
git push origin feature/new-feature
```

5. **Create Pull Request**
- Go to GitHub repository
- Click "Pull requests"
- Click "New pull request"
- Select your branch
- Create PR

6. **PR Validation Runs**
- CloudFormation validation ✅
- Secret scanning ✅
- Template linting ✅
- Results commented on PR

7. **Merge PR**
- Review validation results
- Merge via GitHub UI
- Deploy workflow runs automatically

8. **Monitor Deployment**
- Watch Actions tab
- Check Slack for notification
- Verify in AWS Console

---

## 🛠️ Troubleshooting Guide

### Issue: Workflow Fails

**Solution:**
1. Go to **Actions** tab
2. Click failed workflow
3. Expand failed step
4. Read error message
5. Common issues:
   - Invalid AWS credentials → Check GitHub Secrets
   - CloudFormation error → Validate template
   - Permission denied → Check IAM policy

### Issue: No Slack Notifications

**Solution:**
1. Verify `SLACK_WEBHOOK_URL` secret exists
2. Test webhook manually:
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'
```
3. Check Lambda logs:
```bash
aws logs tail /aws/lambda/rds-scanner-function --follow
```

### Issue: Stack Already Exists

**Solution:**
- This is normal! Workflow handles updates automatically
- No action needed
- Check Actions logs to confirm update succeeded

### Issue: Secrets Not Working

**Solution:**
- Verify secret names match exactly (case-sensitive):
  - ✅ `AWS_ACCESS_KEY_ID`
  - ✅ `AWS_SECRET_ACCESS_KEY`
  - ✅ `SLACK_WEBHOOK_URL`
- Re-create secrets if needed
- Trigger new deployment (push commit)

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] GitHub repository created
- [ ] All files copied to repository
- [ ] AWS credentials obtained
- [ ] Slack webhook created
- [ ] GitHub Secrets configured

### Deployment
- [ ] Files committed to main branch
- [ ] Deploy workflow triggered
- [ ] Workflow completed successfully
- [ ] CloudFormation stack created
- [ ] Lambda function deployed
- [ ] S3 bucket created
- [ ] EventBridge rules configured

### Validation
- [ ] Manual test workflow run
- [ ] Test Lambda function succeeded
- [ ] Slack notification received
- [ ] S3 report generated
- [ ] CloudWatch logs visible

### Scheduled Runs
- [ ] Monday schedule confirmed (9 AM UTC)
- [ ] Friday schedule confirmed (9 AM UTC)
- [ ] First Monday scan successful
- [ ] First Friday scan successful
- [ ] Reports appearing in S3

---

## 🎯 What Happens on Push to Main

```
┌─────────────────────────────────────────────────────────┐
│  You: git push origin main                              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions: Deploy Workflow Triggered              │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 1: Validate CloudFormation Template              │
│  ✅ Template syntax checked                             │
│  ✅ Parameters validated                                │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 2: Create Parameters from Secrets                │
│  ✅ Slack webhook added                                 │
│  ✅ AWS regions configured                              │
│  ✅ Thresholds set                                      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 3: Deploy CloudFormation Stack                   │
│  ✅ Lambda function created                             │
│  ✅ S3 bucket created                                   │
│  ✅ IAM role created                                    │
│  ✅ EventBridge rules created                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 4: Test Lambda Function                          │
│  ✅ Lambda invoked with test payload                    │
│  ✅ Response logged                                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Step 5: Send Slack Notification                       │
│  ✅ Deployment status sent to Slack                     │
│  ✅ Stack outputs displayed                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  Result: Infrastructure Deployed ✅                     │
│  - Scans run Monday & Friday at 9 AM UTC               │
│  - Slack notifications enabled                         │
│  - Reports saved to S3                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 💰 Cost Summary

### AWS Costs (Monthly)
- Lambda: $0.50 (8 runs/month @ 15 min each)
- S3: $0.10 (storage for reports)
- CloudWatch: $0.50 (logs retention)
- Other services: Free tier
- **Total: ~$1-2/month**

### GitHub Actions
- Free for public repositories
- 2,000 minutes/month free for private repos
- This uses ~8 minutes/month
- **Effectively free**

### Potential Savings
- Small team: $300-$500/month
- Medium company: $1,000-$2,000/month
- Enterprise: $5,000-$10,000+/month

**ROI: 500-10,000x** 🎯

---

## 📚 Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| **GITHUB_QUICKSTART.md** | 10-minute setup | 👈 Start here |
| **GITHUB_DEPLOYMENT.md** | Complete guide | Full details |
| **README_GITHUB.md** | Repository README | Use as main README |
| **SLACK_MESSAGE_EXAMPLES.md** | Notification examples | See what Slack looks like |
| **GITHUB_DEPLOYMENT_PACKAGE.md** | This file | Overview |

---

## ✅ Next Steps

1. ✅ Copy all files to your GitHub repository
2. ✅ Configure GitHub Secrets
3. ✅ Push to main branch
4. ✅ Watch GitHub Actions deploy
5. ✅ Test via Actions tab
6. ✅ Wait for Monday scheduled run
7. ✅ Review Slack notification
8. ✅ Download S3 report
9. ✅ Take action on findings
10. ✅ Track cost savings!

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Deploy workflow completes successfully
- ✅ CloudFormation stack shows CREATE_COMPLETE
- ✅ Test workflow sends Slack message
- ✅ Monday 9 AM UTC scan runs automatically
- ✅ Friday 9 AM UTC scan runs automatically
- ✅ Reports appear in S3 bucket
- ✅ Lambda logs visible in CloudWatch
- ✅ Team receives actionable insights

---

**Ready to deploy?**

1. Start with: [GITHUB_QUICKSTART.md](GITHUB_QUICKSTART.md)
2. Configure secrets
3. Push to main
4. Watch the magic happen! ✨

**Questions?**  
Read [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md) for complete details.

**Need help?**  
Check Actions logs, CloudWatch, or CloudFormation events.

---

**Cost:** ~$1-2/month  
**Savings:** $500-$10,000+/month  
**ROI:** 500-10,000x 🚀
