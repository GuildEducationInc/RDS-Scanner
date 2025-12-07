# RDS Scanner - Complete Solution Guide

## 📋 Overview

This is a complete AWS RDS database scanner that identifies unused and underused databases, with automatic Slack notifications.

**⭐ CLOUDFORMATION DEPLOYMENT (RECOMMENDED) ⭐**

**Key Features:**
- ✅ Scans RDS instances across multiple regions
- ✅ Scheduled runs every Monday (with reminder) and Friday
- ✅ Beautiful Slack notifications with actionable insights
- ✅ Detailed CSV reports stored in S3
- ✅ Cost savings estimates
- ✅ Tag tracking (owner, contact, repo)

---

## 🎯 Quick Start - CloudFormation (5 Minutes)

**This is the easiest and recommended method!**

### Step 1: Get Slack Webhook
1. Go to https://api.slack.com/messaging/webhooks
2. Create new webhook → Select channel (#database-ops)
3. Copy the webhook URL

### Step 2: Deploy
```bash
chmod +x deploy.sh
./deploy.sh
```

### Step 3: Test
```bash
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": true}' \
  response.json
```

### Step 4: Check Slack!
You should see a formatted message with database scan results.

**📖 Detailed Guide:** See [README_CLOUDFORMATION.md](README_CLOUDFORMATION.md)

---

## 📁 File Guide

### CloudFormation Deployment Files

| File | Purpose |
|------|---------|
| **README_CLOUDFORMATION.md** | 👈 **START HERE** - Main guide |
| **rds-scanner-cloudformation.yaml** | CloudFormation template |
| **parameters.json** | Configuration file (edit this) |
| **deploy.sh** | Automated deployment script |
| **CFT_DEPLOYMENT_GUIDE.md** | Detailed instructions |
| **SLACK_MESSAGE_EXAMPLES.md** | See what Slack messages look like |

### Local Execution Files (Alternative)

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | Quick start for local execution |
| **README.md** | Complete documentation |
| **rds_scanner.py** | Python scanner script |
| **run.sh** | Convenience script |

---

## 🔍 What This Does

### Scans Your Databases and Identifies:

**🔴 Unused Databases**
- Zero transactions in last 6 months
- **Action:** Delete or archive to save costs

**🟡 Underused Databases**
- CPU < 50% OR transactions < 50/month
- **Action:** Downsize to smaller instance

**🟢 Active Databases**
- Normal usage
- **Action:** None needed

### Sends Slack Notifications:

**Monday 9:00 AM UTC** - With reminder pretext:
```
⏰ REMINDER: Weekly RDS Database Scan
Please review unused and underused databases!

🗄️ RDS Database Scan Results
Total: 25 | Unused: 5 | Underused: 8 | Active: 12
💰 Potential Savings: ~$900/month
```

**Friday 9:00 AM UTC** - Status update (same format, no reminder)

---

## 💰 Cost & ROI

### AWS Costs
**Monthly:** ~$1-2 (Lambda + S3 + CloudWatch)

### Potential Savings
- Small team: $300-$500/month
- Medium company: $1,000-$2,000/month  
- Enterprise: $5,000-$10,000+/month

**ROI: 500-10,000x** 🎯

---

## 📋 What Gets Deployed (CloudFormation)

When you run `./deploy.sh`, it creates:

- ✅ Lambda Function (scans RDS databases)
- ✅ S3 Bucket (stores CSV reports)
- ✅ EventBridge Rules (Mon & Fri schedules)
- ✅ IAM Role (with required permissions)
- ✅ CloudWatch Log Group (for monitoring)

**Total Time:** 2-3 minutes to deploy
**Total Cost:** ~$1-2/month

---

## 🎛️ Configuration

Edit `parameters.json` to customize:

```json
{
  "SlackWebhookURL": "https://hooks.slack.com/services/YOUR/WEBHOOK",
  "ScanRegions": "us-east-1,us-west-2,eu-west-1",
  "CPUThreshold": "50",
  "TransactionThreshold": "50"
}
```

**Configurable:**
- Which regions to scan
- CPU threshold for underused databases
- Transaction threshold
- Report retention period
- Lambda memory and timeout

---

## 📖 Documentation Map

### 🏁 Getting Started
1. **START_HERE.md** ← You are here!
2. **[README_CLOUDFORMATION.md](README_CLOUDFORMATION.md)** ← Go here next!
3. **[deploy.sh](deploy.sh)** ← Run this to deploy

### 🔧 Deployment Guides
- **[CFT_DEPLOYMENT_GUIDE.md](CFT_DEPLOYMENT_GUIDE.md)** - Detailed CloudFormation guide
- **[LAMBDA_DEPLOYMENT.md](LAMBDA_DEPLOYMENT.md)** - Manual Lambda setup
- **[QUICKSTART.md](QUICKSTART.md)** - Local execution guide

### 💬 Slack Integration
- **[SLACK_MESSAGE_EXAMPLES.md](SLACK_MESSAGE_EXAMPLES.md)** - See message examples

### 📚 Reference
- **[README.md](README.md)** - Complete documentation
- **[iam_policy.json](iam_policy.json)** - IAM permissions
- **[parameters.json](parameters.json)** - Configuration template

---

## ⚡ Deployment Options Comparison

| Feature | CloudFormation | Local Execution | Terraform |
|---------|---------------|-----------------|-----------|
| **Setup Time** | 5 minutes | 5 minutes | 15 minutes |
| **Automated Schedule** | ✅ Yes | ❌ No | ✅ Yes |
| **Slack Notifications** | ✅ Yes | ❌ No | ✅ Yes |
| **Maintenance** | Low | Manual | Low |
| **Best For** | Production | Testing | Teams using Terraform |

**Recommendation:** Use CloudFormation for production deployments.

---

## 🚀 Quick Deploy (Repeat)

```bash
# 1. Get Slack webhook from https://api.slack.com/messaging/webhooks

# 2. Run deployment script
./deploy.sh

# 3. Test it
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": true}' \
  response.json

# 4. Check Slack for your report!
```

---

## 🛠️ Troubleshooting

### Deployment Issues
**Problem:** Stack creation fails
**Solution:** Check `parameters.json` has valid values

**Problem:** No Slack webhook
**Solution:** Visit https://api.slack.com/messaging/webhooks

### Runtime Issues
**Problem:** No Slack messages
**Solution:** Check Lambda logs:
```bash
aws logs tail /aws/lambda/rds-scanner-function --follow
```

**Problem:** No databases found
**Solution:** Verify regions in `parameters.json`

**Problem:** Permission denied
**Solution:** Apply IAM policy from `iam_policy.json`

---

## ✅ Success Checklist

- [ ] Got Slack webhook URL
- [ ] Edited `parameters.json`
- [ ] Ran `./deploy.sh`
- [ ] Stack created successfully
- [ ] Tested Lambda function
- [ ] Received Slack message
- [ ] Reviewed S3 report
- [ ] Scheduled runs confirmed (Mon & Fri)

---

## 📞 Next Steps

### Just Getting Started?
👉 **Go to: [README_CLOUDFORMATION.md](README_CLOUDFORMATION.md)**

### Want to Test Locally First?
👉 **Go to: [QUICKSTART.md](QUICKSTART.md)**

### Need to Customize?
👉 **Edit: [parameters.json](parameters.json)**
👉 **Read: [CFT_DEPLOYMENT_GUIDE.md](CFT_DEPLOYMENT_GUIDE.md)**

### Want to See Slack Examples?
👉 **Go to: [SLACK_MESSAGE_EXAMPLES.md](SLACK_MESSAGE_EXAMPLES.md)**

---

## 🎯 Why Use This?

1. **💰 Save Money** - Identify unused databases costing thousands/month
2. **📊 Visibility** - Know what databases you have and their usage
3. **🏷️ Accountability** - Track ownership through tags
4. **⚡ Automated** - Runs automatically, no manual work
5. **💬 Notifications** - Team gets updates in Slack
6. **📈 Actionable** - Clear recommendations on what to do

---

**Ready to start saving money? Deploy now!**

```bash
./deploy.sh
```

**Questions? Check [README_CLOUDFORMATION.md](README_CLOUDFORMATION.md) for complete guide.**
