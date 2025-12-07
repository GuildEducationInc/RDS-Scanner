# RDS Scanner Lambda Deployment Setup

This guide explains how to deploy the RDS Scanner Lambda function using GitHub Actions with AWS OIDC authentication.

## Overview

The RDS Scanner Lambda deployment is automated through GitHub Actions workflow located at `.github/workflows/deploy-rds-scanner.yml`. The workflow:

- Uses **AWS OIDC** (OpenID Connect) for secure authentication without long-lived credentials
- Supports **multi-account deployments** (development, staging, production)
- Validates the CloudFormation template
- Deploys/updates the Lambda function and associated AWS resources
- Tests the Lambda function after deployment
- Sends Slack notifications on deployment status

## Authentication Method

This workflow uses **GitHub OIDC** to assume AWS IAM roles, following Guild's DevOps best practices. This eliminates the need for storing AWS access keys as GitHub secrets.

### AWS Account & Role Mapping

The workflow automatically assumes the appropriate IAM role based on the deployment environment:

| Environment | AWS Account | IAM Role ARN | Stack Name |
|-------------|-------------|--------------|------------|
| **Development** | 477873552632 (guild-dev) | `arn:aws:iam::477873552632:role/devops-deploy-role` | rds-scanner-dev |
| **Staging** | 221203628080 (guild-staging) | `arn:aws:iam::221203628080:role/devops-deploy-role` | rds-scanner-staging |
| **Production** | 947618278001 (guild-prod) | `arn:aws:iam::947618278001:role/devops-deploy-role` | rds-scanner-prod |

**Note:** The `devops-deploy-role` must already exist in each AWS account with the necessary permissions and a trust relationship configured for GitHub OIDC. Contact DevOps if you need assistance setting this up.

## Required GitHub Secrets

Before deploying, you must configure the following secrets in your GitHub repository:

### Go to: Settings → Secrets and variables → Actions → New repository secret

### Required Secrets

1. **SLACK_WEBHOOK_URL**
   - Slack incoming webhook URL for notifications
   - Format: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
   - How to create: See [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)

### Optional Secrets

2. **SCAN_REGIONS** (Optional)
   - Comma-separated list of AWS regions to scan for RDS instances
   - Default: `us-east-1,us-west-2`
   - Example: `us-east-1,us-west-2,eu-west-1,ap-southeast-1`

## How to Deploy

### Automatic Deployment to Development

The workflow automatically deploys to the **development** environment when you push changes to:
- `main` branch
- `dsd-258` branch (current feature branch)
- And the following files are modified:
  - `rds-scanner-complete/rds-scanner-cloudformation.yaml`
  - `rds-scanner-complete/parameters.json`
  - `.github/workflows/deploy-rds-scanner.yml`

Simply push your changes:

```bash
git add .
git commit -m "Update RDS Scanner Lambda"
git push origin dsd-258
```

This will automatically deploy to the **guild-dev** AWS account (477873552632).

### Manual Deployment to Staging or Production

For staging or production deployments, use manual workflow dispatch:

1. Go to **Actions** tab in your GitHub repository
2. Select **Deploy RDS Scanner Lambda to AWS** workflow
3. Click **Run workflow** button
4. **Select environment:**
   - **development** → Deploys to guild-dev (477873552632)
   - **staging** → Deploys to guild-staging (221203628080)
   - **production** → Deploys to guild-prod (947618278001)
5. Click **Run workflow**

## Deployment Process

The workflow executes the following jobs:

### 1. Validate Job
- Checks out the code
- Sets environment variables (determines target AWS account)
- **Assumes AWS IAM role** using OIDC (no access keys needed!)
- Validates CloudFormation template syntax

### 2. Deploy Job
- Checks out the code
- Sets environment variables (determines target AWS account)
- **Assumes AWS IAM role** using OIDC
- Creates parameters file with Slack webhook and scan regions
- Creates or updates the CloudFormation stack with:
  - Lambda function (Python 3.9, 512 MB, 900s timeout)
  - IAM role with required permissions for RDS/CloudWatch/S3
  - S3 bucket for reports (encrypted, versioned, 90-day lifecycle)
  - CloudWatch log group (30-day retention)
  - EventBridge rules for scheduled execution (Monday & Friday at 9 AM UTC)
- Tests the Lambda function with a test invocation
- Uploads test results as artifacts

### 3. Notify Job
- Sets environment variables
- Sends deployment status to Slack (if webhook is configured)
- Includes deployment details: environment, stack name, repository, branch, commit, actor

## Monitoring Deployment

### GitHub Actions UI
- View real-time logs in the **Actions** tab
- Check job summaries for stack outputs and test results
- Download test response artifacts

### AWS Console
- **CloudFormation**: Monitor stack creation/update progress
- **Lambda**: View function configuration and test invocations
- **CloudWatch Logs**: Check Lambda execution logs
- **S3**: View generated reports

## Stack Outputs

After successful deployment, the workflow displays these outputs:

- **LambdaFunctionName**: Name of the deployed Lambda function
- **LambdaFunctionArn**: ARN of the Lambda function
- **ReportsBucket**: S3 bucket where reports are stored
- **ScheduleRules**: EventBridge rules for automated execution

## Troubleshooting

### Deployment Fails with "User is not authorized to perform: sts:AssumeRoleWithWebIdentity"

This means the GitHub OIDC trust relationship is not configured for the IAM role in the target AWS account. Contact DevOps to ensure:
1. The `devops-deploy-role` exists in the target AWS account
2. The role has a trust relationship configured for GitHub OIDC
3. The trust policy includes your repository in the allowed subjects

### Deployment Fails with IAM Permissions Error

Ensure the `devops-deploy-role` in the target AWS account has the required permissions:
- CloudFormation: CreateStack, UpdateStack, DescribeStacks, DeleteStack
- Lambda: CreateFunction, UpdateFunctionCode, UpdateFunctionConfiguration, InvokeFunction
- IAM: CreateRole, AttachRolePolicy, PutRolePolicy, PassRole
- S3: CreateBucket, PutObject, PutBucketPolicy, PutEncryptionConfiguration
- CloudWatch: CreateLogGroup, PutRetentionPolicy
- EventBridge: PutRule, PutTargets

Recommended: Attach the `PowerUserAccess` managed policy or a custom policy with these permissions.

### Template Validation Fails

Check the CloudFormation template syntax:
```bash
cd rds-scanner-complete
aws cloudformation validate-template --template-body file://rds-scanner-cloudformation.yaml
```

### Lambda Test Fails

Check Lambda execution logs in CloudWatch:
```bash
aws logs tail /aws/lambda/rds-scanner --follow
```

### No Slack Notifications

Verify:
1. `SLACK_WEBHOOK_URL` secret is correctly configured
2. The webhook URL is valid and accessible
3. Check workflow logs for Slack notification step errors

## Customization

### Change AWS Region

The workflow deploys to `us-west-2` by default. To change the region, edit `.github/workflows/deploy-rds-scanner.yml`:
```yaml
env:
  AWS_REGION: us-east-1  # Change to desired region
```

### Change Stack Names

Stack names are environment-specific and set automatically:
- Development: `rds-scanner-dev`
- Staging: `rds-scanner-staging`
- Production: `rds-scanner-prod`

To customize, edit the `Set environment variables` step in `.github/workflows/deploy-rds-scanner.yml`.

### Modify Lambda Configuration

Edit parameters in the workflow file's "Create parameters file" step:
- `LambdaTimeout`: Execution timeout (seconds) - default: 900
- `LambdaMemorySize`: Memory allocation (MB) - default: 512
- `CPUThreshold`: CPU threshold for categorization (%) - default: 50
- `TransactionThreshold`: Transaction threshold for categorization - default: 50

Or create a `SCAN_REGIONS` secret to customize which AWS regions to scan.

### Deploy to Different AWS Accounts

To use different AWS accounts, update the IAM role ARNs in the `Set environment variables` step:
```yaml
case $ENV in
  production)
    echo "ROLE_ARN=arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_ROLE_NAME" >> $GITHUB_OUTPUT
    ;;
esac
```

## Security Best Practices

1. **OIDC Authentication** ✅ This workflow already uses GitHub OIDC instead of long-lived AWS credentials
2. **Least Privilege**: The `devops-deploy-role` should follow the principle of least privilege
3. **No Hardcoded Secrets**: All sensitive values are stored in GitHub Secrets
4. **Environment Isolation** ✅ Separate AWS accounts for dev/staging/production
5. **Audit Trail**: All deployments are tracked in GitHub Actions with full audit logs
6. **Immutable Infrastructure**: Infrastructure is defined as code in CloudFormation templates

## Cost Estimate

Estimated monthly AWS costs:
- Lambda: ~$0.50 (8 invocations × 15 min each)
- S3: ~$0.10 (report storage)
- CloudWatch Logs: ~$0.50
- **Total: ~$1-2/month**

## Additional Resources

- [RDS Scanner Documentation](../rds-scanner-complete/README.md)
- [CloudFormation Deployment Guide](../rds-scanner-complete/CFT_DEPLOYMENT_GUIDE.md)
- [Slack Integration Guide](../rds-scanner-complete/SLACK_INTEGRATION.md)
- [AWS CloudFormation Documentation](https://docs.aws.amazon.com/cloudformation/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
