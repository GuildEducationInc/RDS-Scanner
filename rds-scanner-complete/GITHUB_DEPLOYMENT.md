# GitHub Deployment Guide - RDS Scanner

Deploy the RDS Scanner to AWS using GitHub Actions for automated CloudFormation deployment.

## 🎯 Overview

This solution uses **GitHub Actions** to automatically deploy and manage your RDS Scanner infrastructure:

- ✅ **Automated Deployment** - Push to main branch to deploy
- ✅ **Infrastructure as Code** - CloudFormation in version control
- ✅ **Secrets Management** - GitHub Secrets for sensitive data
- ✅ **CI/CD Pipeline** - Validate, test, and deploy automatically
- ✅ **Manual Triggers** - Test Lambda function on-demand
- ✅ **Safe Deletion** - Controlled stack removal workflow

---

## 🚀 Quick Setup (10 Minutes)

### Step 1: Fork/Clone Repository

```bash
# Create a new repository on GitHub
# Then clone it locally
git clone https://github.com/YOUR_USERNAME/rds-scanner.git
cd rds-scanner
```

### Step 2: Add Files to Repository

Copy these files to your repository:
- `rds-scanner-cloudformation.yaml`
- `.github/workflows/deploy.yml`
- `.github/workflows/test.yml`
- `.github/workflows/destroy.yml`
- `.github/workflows/pr-validation.yml`
- `.gitignore`

```bash
# Add and commit files
git add .
git commit -m "Initial commit: RDS Scanner with GitHub Actions"
```

### Step 3: Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

#### Required Secrets

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | `https://hooks.slack.com/services/XXX/YYY/ZZZ` |

#### Optional Secrets

| Secret Name | Description | Default |
|-------------|-------------|---------|
| `SCAN_REGIONS` | Comma-separated AWS regions | `us-east-1,us-west-2` |

### Step 4: Push to GitHub

```bash
git push origin main
```

**That's it!** GitHub Actions will automatically deploy the stack.

---

## 📋 GitHub Actions Workflows

### 1. Deploy Workflow (`.github/workflows/deploy.yml`)

**Triggers:**
- Push to `main` or `production` branch
- Manual trigger via "Actions" tab

**What it does:**
1. ✅ Validates CloudFormation template
2. ✅ Creates parameters from GitHub Secrets
3. ✅ Deploys or updates CloudFormation stack
4. ✅ Tests Lambda function
5. ✅ Sends deployment notification to Slack

**View in GitHub:**
- Go to **Actions** tab
- See deployment status and logs

### 2. Test Workflow (`.github/workflows/test.yml`)

**Triggers:**
- Manual trigger only

**What it does:**
1. ✅ Invokes Lambda function
2. ✅ Displays response and logs
3. ✅ Uploads test results as artifacts
4. ✅ Notifies Slack of test results

**How to use:**
1. Go to **Actions** tab
2. Select "Test RDS Scanner"
3. Click "Run workflow"
4. Choose test type (Monday with reminder or Friday)
5. Click "Run workflow"

### 3. Destroy Workflow (`.github/workflows/destroy.yml`)

**Triggers:**
- Manual trigger only (safety measure)

**What it does:**
1. ✅ Validates deletion confirmation
2. ✅ Empties S3 bucket
3. ✅ Deletes CloudFormation stack
4. ✅ Notifies Slack of deletion

**How to use:**
1. Go to **Actions** tab
2. Select "Destroy RDS Scanner Stack"
3. Click "Run workflow"
4. Type `DELETE` in confirmation field
5. Check "Empty S3 bucket"
6. Click "Run workflow"

⚠️ **Warning:** This permanently deletes all resources!

### 4. PR Validation Workflow (`.github/workflows/pr-validation.yml`)

**Triggers:**
- Pull requests to `main` or `production` branch

**What it does:**
1. ✅ Validates CloudFormation template
2. ✅ Checks for hardcoded secrets
3. ✅ Lints CloudFormation
4. ✅ Comments results on PR

---

## 🔑 Setting Up GitHub Secrets

### AWS Credentials

**Option 1: IAM User (Recommended for Testing)**

1. Create IAM user in AWS Console
2. Attach policy from `iam_policy.json` + CloudFormation permissions
3. Generate access keys
4. Add to GitHub Secrets

**Required IAM Permissions:**
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
        "events:*"
      ],
      "Resource": "*"
    }
  ]
}
```

**Option 2: OIDC (Recommended for Production)**

Use GitHub's OIDC provider to assume an IAM role (more secure, no long-lived credentials).

[GitHub OIDC Setup Guide](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

### Slack Webhook URL

1. Go to https://api.slack.com/messaging/webhooks
2. Create new webhook
3. Select channel (e.g., `#database-ops`)
4. Copy webhook URL
5. Add to GitHub Secrets as `SLACK_WEBHOOK_URL`

---

## 📁 Repository Structure

```
rds-scanner/
├── .github/
│   └── workflows/
│       ├── deploy.yml           # Main deployment workflow
│       ├── test.yml             # Manual testing workflow
│       ├── destroy.yml          # Stack deletion workflow
│       └── pr-validation.yml    # PR validation workflow
├── .gitignore                   # Git ignore file
├── rds-scanner-cloudformation.yaml  # CloudFormation template
├── README.md                    # This file
└── GITHUB_DEPLOYMENT.md         # Detailed guide
```

---

## 🎬 Usage Examples

### Deploy to Production

```bash
# Make changes to CloudFormation template
vim rds-scanner-cloudformation.yaml

# Commit and push
git add rds-scanner-cloudformation.yaml
git commit -m "Update CPU threshold to 40%"
git push origin main

# GitHub Actions automatically deploys!
```

### Test Lambda Function

**Via GitHub Actions:**
1. Go to **Actions** tab
2. Select "Test RDS Scanner"
3. Click "Run workflow"
4. Choose Monday or Friday test
5. View results in Slack and GitHub

**Via AWS CLI (locally):**
```bash
aws lambda invoke \
  --function-name rds-scanner-function \
  --payload '{"is_monday": true}' \
  response.json
```

### Update Configuration

**Update Scan Regions:**
1. Go to **Settings → Secrets → Actions**
2. Update `SCAN_REGIONS` secret
3. Trigger redeployment by pushing a commit

**Update Slack Webhook:**
1. Go to **Settings → Secrets → Actions**
2. Update `SLACK_WEBHOOK_URL` secret
3. Trigger redeployment

### Create Feature Branch

```bash
# Create feature branch
git checkout -b feature/update-thresholds

# Make changes
vim rds-scanner-cloudformation.yaml

# Commit and push
git add .
git commit -m "Update CPU threshold to 40%"
git push origin feature/update-thresholds

# Create PR on GitHub
# PR validation workflow runs automatically
```

---

## 🔍 Monitoring Deployments

### View Workflow Runs

1. Go to **Actions** tab in GitHub
2. Click on workflow run
3. View logs for each step
4. Download artifacts (test results)

### View CloudFormation Stack

```bash
# Via AWS CLI
aws cloudformation describe-stacks --stack-name rds-scanner

# Via AWS Console
# CloudFormation → Stacks → rds-scanner
```

### View Lambda Logs

```bash
# Via AWS CLI
aws logs tail /aws/lambda/rds-scanner-function --follow

# Via AWS Console
# CloudWatch → Log groups → /aws/lambda/rds-scanner-function
```

### View S3 Reports

```bash
# List reports
aws s3 ls s3://rds-scanner-reports-ACCOUNT-ID/rds-scans/

# Download latest report
aws s3 cp s3://rds-scanner-reports-ACCOUNT-ID/rds-scans/ ./ --recursive
```

---

## 🔒 Security Best Practices

### 1. Use GitHub Secrets
✅ Never commit AWS credentials  
✅ Never commit Slack webhooks  
✅ Use `.gitignore` to prevent accidental commits  

### 2. Branch Protection
Enable branch protection on `main`:
- Require PR reviews
- Require status checks to pass
- Prevent force pushes

### 3. OIDC Instead of Access Keys
For production, use GitHub OIDC to assume IAM roles instead of access keys.

### 4. Least Privilege IAM
Grant only necessary permissions to the IAM user/role.

### 5. Audit Logs
Monitor CloudTrail and GitHub Actions logs for unauthorized access.

---

## 🛠️ Troubleshooting

### Deployment Fails

**Check workflow logs:**
1. Go to **Actions** tab
2. Click failed workflow
3. Expand failed step
4. Review error messages

**Common issues:**
- Invalid AWS credentials → Check GitHub Secrets
- Stack already exists → Workflow handles updates automatically
- Template validation error → Check CloudFormation syntax
- Permission denied → Update IAM policy

### Test Workflow Fails

**Check Lambda logs:**
```bash
aws logs tail /aws/lambda/rds-scanner-function --since 1h
```

**Common issues:**
- Lambda timeout → Increase timeout in template
- No databases found → Check scan regions
- Slack notification fails → Verify webhook URL

### Can't Access GitHub Secrets

**Verify secret names match exactly:**
- `AWS_ACCESS_KEY_ID` (not `AWS_ACCESS_KEY`)
- `AWS_SECRET_ACCESS_KEY` (not `AWS_SECRET_KEY`)
- `SLACK_WEBHOOK_URL` (not `SLACK_WEBHOOK`)

### Stack Deletion Fails

**Manually empty S3 bucket:**
```bash
aws s3 rm s3://rds-scanner-reports-ACCOUNT-ID --recursive
```

**Then rerun destroy workflow**

---

## 🔄 Update Workflow

### Update CloudFormation Template

```bash
# 1. Create feature branch
git checkout -b update/new-feature

# 2. Edit template
vim rds-scanner-cloudformation.yaml

# 3. Commit and push
git add rds-scanner-cloudformation.yaml
git commit -m "Add new feature"
git push origin update/new-feature

# 4. Create PR
# PR validation runs automatically

# 5. Merge PR
# Deploy workflow runs automatically
```

### Update GitHub Actions Workflow

```bash
# Edit workflow
vim .github/workflows/deploy.yml

# Commit and push
git add .github/workflows/deploy.yml
git commit -m "Update deployment workflow"
git push origin main
```

---

## 📊 Monitoring & Alerts

### Slack Notifications

You'll receive Slack notifications for:
- ✅ Successful deployments
- ❌ Failed deployments
- 🧪 Manual test results
- 🗑️ Stack deletions

### GitHub Notifications

GitHub will notify you (via email/app) for:
- Workflow failures
- PR checks
- Successful deployments

### AWS Monitoring

Monitor via:
- CloudWatch Logs (Lambda execution logs)
- CloudFormation Events (stack changes)
- S3 (generated reports)

---

## 🎯 Advanced Configuration

### Multi-Environment Deployment

Create separate workflows for dev, staging, prod:

```yaml
# .github/workflows/deploy-prod.yml
on:
  push:
    branches:
      - production

env:
  STACK_NAME: rds-scanner-prod
  AWS_REGION: us-east-1
```

### Scheduled Deployments

Add cron schedule to workflow:

```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # Deploy every Sunday at midnight
```

### Slack Approval for Production

Use GitHub Environments with required reviewers:

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://console.aws.amazon.com/cloudformation
```

---

## 📚 Additional Resources

### GitHub Actions
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS Actions](https://github.com/aws-actions)
- [GitHub OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

### AWS CloudFormation
- [CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [CloudFormation Best Practices](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/best-practices.html)

### Security
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

## ✅ Deployment Checklist

- [ ] Repository created on GitHub
- [ ] Files added and committed
- [ ] AWS credentials added to GitHub Secrets
- [ ] Slack webhook added to GitHub Secrets
- [ ] Branch protection enabled on main
- [ ] First deployment triggered (push to main)
- [ ] Deployment successful (check Actions tab)
- [ ] Lambda function tested (manual workflow)
- [ ] Slack notification received
- [ ] S3 report generated
- [ ] Scheduled runs confirmed (Mon & Fri)

---

## 🎉 Next Steps

1. ✅ Complete setup checklist above
2. ✅ Test deployment with feature branch
3. ✅ Monitor first automated scan (Monday)
4. ✅ Review reports in S3
5. ✅ Set up branch protection
6. ✅ Configure multi-environment if needed
7. ✅ Document team workflow

---

**Questions?**  
- Check GitHub Actions logs
- Review CloudFormation events
- Inspect Lambda logs in CloudWatch

**Ready to deploy?**  
Push to main and watch GitHub Actions handle everything! 🚀
