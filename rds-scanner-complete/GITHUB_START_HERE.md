# 🚀 GitHub Deployment - START HERE

## ⚡ Deploy to AWS via GitHub Actions in 10 Minutes!

This package contains everything you need for automated GitHub-based deployment.

---

## 📦 What You're Getting

Complete CI/CD solution that:
- ✅ Deploys on push to main branch
- ✅ Schedules scans every Monday (with reminder) & Friday
- ✅ Sends Slack notifications automatically
- ✅ Stores reports in S3
- ✅ Tests Lambda functions
- ✅ Validates pull requests

---

## 🎯 Quick Start (3 Steps)

### Step 1: Create GitHub Repository

```bash
# On GitHub.com, click "New Repository"
# Name: rds-scanner
# Public or Private: Your choice
# Initialize: Leave unchecked

# Clone locally
git clone https://github.com/YOUR_USERNAME/rds-scanner.git
cd rds-scanner
```

### Step 2: Copy These Files

Copy to your repository root:

**Required Files:**
```
rds-scanner-cloudformation.yaml    ← CloudFormation template
.github/workflows/deploy.yml       ← Main deployment
.github/workflows/test.yml         ← Testing workflow
.github/workflows/destroy.yml      ← Stack deletion
.github/workflows/pr-validation.yml ← PR validation
.gitignore                         ← Git ignore rules
README_GITHUB.md                   ← Rename to README.md
```

**Documentation (Recommended):**
```
GITHUB_QUICKSTART.md               ← 10-minute guide
GITHUB_DEPLOYMENT.md               ← Full documentation
GITHUB_DEPLOYMENT_PACKAGE.md       ← Complete overview
SLACK_MESSAGE_EXAMPLES.md          ← Notification examples
```

### Step 3: Configure & Deploy

**A. Add GitHub Secrets:**

Go to: **Your Repo → Settings → Secrets and variables → Actions**

Add these 3 secrets:

1. **AWS_ACCESS_KEY_ID**
   - Value: Your AWS access key (e.g., AKIAIOSFODNN7EXAMPLE)
   - Get from: AWS IAM Console

2. **AWS_SECRET_ACCESS_KEY**
   - Value: Your AWS secret key
   - Get from: AWS IAM Console

3. **SLACK_WEBHOOK_URL**
   - Value: Your Slack webhook URL
   - Get from: https://api.slack.com/messaging/webhooks

**B. Deploy:**

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: RDS Scanner with GitHub Actions"

# Push to trigger deployment
git push origin main
```

**C. Watch It Deploy:**

1. Go to **Actions** tab in GitHub
2. Watch "Deploy RDS Scanner to AWS" workflow
3. See it complete successfully ✅
4. Check Slack for deployment notification
5. Done! 🎉

---

## 📁 GitHub Repository Structure

After setup, your repository will look like:

```
rds-scanner/                              ← Your GitHub repo
├── .github/
│   └── workflows/
│       ├── deploy.yml                    ← 🚀 Auto-deploy on push
│       ├── test.yml                      ← 🧪 Manual testing
│       ├── destroy.yml                   ← 🗑️ Safe deletion
│       └── pr-validation.yml             ← ✅ PR checks
├── .gitignore                            ← 🚫 Ignore rules
├── rds-scanner-cloudformation.yaml       ← 📋 Infrastructure
├── README.md                             ← 📖 Main docs
├── GITHUB_QUICKSTART.md                  ← ⚡ Quick guide
├── GITHUB_DEPLOYMENT.md                  ← 📚 Full guide
├── GITHUB_DEPLOYMENT_PACKAGE.md          ← 📦 Package overview
└── SLACK_MESSAGE_EXAMPLES.md             ← 💬 Slack examples
```

---

## 🎬 What Happens After Push

```
1. You push to main branch
   ↓
2. GitHub Actions triggers automatically
   ↓
3. Validates CloudFormation template ✅
   ↓
4. Creates AWS resources:
   - Lambda function
   - S3 bucket
   - EventBridge schedules (Mon & Fri)
   - IAM role
   - CloudWatch logs
   ↓
5. Tests Lambda function ✅
   ↓
6. Sends Slack notification ✅
   ↓
7. Done! Infrastructure is live 🎉
```

**Time:** 3-4 minutes  
**Cost:** ~$1-2/month

---

## 💬 What You'll See in Slack

### After Deployment:
```
✅ RDS Scanner Deployment
Deployment Status: Success
Repository: your-org/rds-scanner
Branch: main
```

### Monday 9:00 AM UTC:
```
⏰ REMINDER: Weekly RDS Database Scan
Please review unused and underused databases!

🗄️ RDS Database Scan Results
Total: 25 | Unused: 5 | Underused: 8 | Active: 12
💰 Potential Savings: ~$900/month
```

### Friday 9:00 AM UTC:
Same scan, without reminder pretext.

---

## 🎮 Using GitHub Actions

### Test Manually

1. Go to **Actions** tab
2. Click "Test RDS Scanner"
3. Click "Run workflow"
4. Choose Monday or Friday test
5. Click "Run workflow"
6. Check Slack for test message!

### View Deployment Status

1. Go to **Actions** tab
2. See all workflow runs
3. Click any run to view details
4. Download artifacts (test results)

### Update Configuration

```bash
# Make changes
vim rds-scanner-cloudformation.yaml

# Commit and push
git commit -am "Update configuration"
git push origin main

# Deployment happens automatically!
```

---

## 📊 What Gets Deployed

| AWS Resource | Description |
|--------------|-------------|
| **Lambda Function** | Scans RDS databases |
| **S3 Bucket** | Stores CSV reports (90-day retention) |
| **EventBridge Rules** | Monday & Friday 9 AM UTC schedules |
| **IAM Role** | Lambda execution permissions |
| **CloudWatch Logs** | 30-day log retention |

**Total Cost:** ~$1-2/month  
**Potential Savings:** $500-$10,000+/month  
**ROI:** 500-10,000x 🎯

---

## 🔑 Getting GitHub Secrets

### 1. AWS Credentials

**Step-by-step:**
1. AWS Console → IAM → Users
2. Click "Create user" or select existing
3. Click "Security credentials"
4. Click "Create access key"
5. Choose "Application running outside AWS"
6. Copy both keys

**Permissions needed:**
- CloudFormation (all)
- Lambda (all)
- IAM (all)
- S3 (all)
- EventBridge (all)
- RDS (read)
- CloudWatch (read)

### 2. Slack Webhook

**Step-by-step:**
1. Visit: https://api.slack.com/messaging/webhooks
2. Click "Create your Slack app"
3. Choose "From scratch"
4. Name: "RDS Scanner"
5. Select workspace
6. Click "Incoming Webhooks"
7. Toggle "Activate Incoming Webhooks" ON
8. Click "Add New Webhook to Workspace"
9. Select channel (e.g., #database-ops)
10. Click "Allow"
11. Copy webhook URL

**URL format:**
```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] GitHub Actions workflow completed successfully
- [ ] CloudFormation stack shows "CREATE_COMPLETE"
- [ ] Lambda function exists in AWS
- [ ] S3 bucket created
- [ ] EventBridge rules configured
- [ ] Manual test sends Slack message
- [ ] Scheduled run confirmed for Monday
- [ ] Scheduled run confirmed for Friday

---

## 🛠️ Troubleshooting

### Deployment Fails

**Check Actions logs:**
1. Actions tab → Failed workflow
2. Expand failed step
3. Read error message

**Common issues:**
- ❌ Invalid credentials → Verify GitHub Secrets
- ❌ Permission denied → Check IAM policy
- ❌ Template error → Validate CloudFormation

### No Slack Messages

**Test webhook:**
```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'
```

**Check Lambda logs:**
```bash
aws logs tail /aws/lambda/rds-scanner-function --follow
```

### Secrets Not Working

Verify exact names (case-sensitive):
- `AWS_ACCESS_KEY_ID` ✅
- `AWS_SECRET_ACCESS_KEY` ✅
- `SLACK_WEBHOOK_URL` ✅

---

## 📚 Full Documentation

### Quick Guides
- **GITHUB_QUICKSTART.md** - 10-minute setup ⚡
- **GITHUB_START_HERE.md** - This file 📍

### Complete Guides
- **GITHUB_DEPLOYMENT.md** - Full deployment guide 📚
- **GITHUB_DEPLOYMENT_PACKAGE.md** - Complete overview 📦

### Reference
- **SLACK_MESSAGE_EXAMPLES.md** - Notification examples 💬
- **README_GITHUB.md** - Repository README 📖

---

## 🎯 Next Steps

1. ✅ Create GitHub repository
2. ✅ Copy files to repository
3. ✅ Configure GitHub Secrets
4. ✅ Push to main branch
5. ✅ Watch deployment in Actions tab
6. ✅ Run manual test
7. ✅ Wait for Monday scan
8. ✅ Review Slack notification
9. ✅ Download S3 report
10. ✅ Take action & save money!

---

## 🎉 Success!

When everything is working:

✅ Push to main → Automatic deployment  
✅ Monday 9 AM → Scan with reminder  
✅ Friday 9 AM → Regular scan  
✅ Reports in S3 → Historical tracking  
✅ Slack notifications → Team visibility  
✅ Cost savings → $500-$10,000+/month  

---

**Ready to deploy?**

1. Copy files
2. Add GitHub Secrets
3. Push to main
4. Done! 🚀

**Questions?**  
Read [GITHUB_QUICKSTART.md](GITHUB_QUICKSTART.md) or [GITHUB_DEPLOYMENT.md](GITHUB_DEPLOYMENT.md)

**Start now and save money today!** 💰
