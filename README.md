# RDS Scanner

Automated tool to scan AWS RDS instances across multiple regions, analyze their utilization, and identify unused or underused databases for cost optimization.

## Features

- Multi-region RDS scanning
- CloudWatch metrics analysis (CPU, IOPS)
- Database categorization (Unused/Underused/Active)
- Automated deployment via GitHub Actions
- Slack notifications
- S3 report storage

## Project Structure

```
.
├── .github/
│   ├── workflows/
│   │   └── deploy-rds-scanner.yml    # GitHub Actions deployment workflow
│   └── DEPLOYMENT_SETUP.md            # Deployment documentation
└── rds-scanner-complete/              # RDS Scanner Lambda function
    ├── rds-scanner-cloudformation.yaml
    ├── lambda_handler.py
    ├── rds_scanner.py
    └── documentation/
```

## Quick Start

### GitHub Actions Deployment (Recommended)

1. **Configure GitHub Secrets:**
   - Go to Settings → Secrets and variables → Actions
   - Add `SLACK_WEBHOOK_URL` secret

2. **Deploy:**
   - Push changes to trigger automatic deployment to development
   - Or manually trigger workflow for staging/production

See [Deployment Setup Guide](.github/DEPLOYMENT_SETUP.md) for detailed instructions.

### Manual Deployment

```bash
cd rds-scanner-complete
./deploy.sh
```

## Documentation

- [Deployment Setup](.github/DEPLOYMENT_SETUP.md) - GitHub Actions deployment guide
- [RDS Scanner Complete](rds-scanner-complete/README.md) - Full project documentation
- [CloudFormation Guide](rds-scanner-complete/CFT_DEPLOYMENT_GUIDE.md) - CloudFormation deployment
- [Slack Integration](rds-scanner-complete/SLACK_INTEGRATION.md) - Slack setup guide

## Architecture

- **Lambda Function**: Serverless execution (Python 3.9)
- **CloudFormation**: Infrastructure as Code
- **EventBridge**: Scheduled execution (Monday & Friday, 9 AM UTC)
- **S3**: Report storage
- **CloudWatch**: Metrics and logs
- **GitHub Actions**: CI/CD with OIDC authentication

## AWS Accounts

The deployment supports multi-account environments:

| Environment | AWS Account | Stack Name |
|-------------|-------------|------------|
| Development | 477873552632 (guild-dev) | rds-scanner-dev |
| Staging | 221203628080 (guild-staging) | rds-scanner-staging |
| Production | 947618278001 (guild-prod) | rds-scanner-prod |

## Cost Estimate

Estimated monthly AWS costs: **$1-2/month**
- Lambda: ~$0.50
- S3: ~$0.10
- CloudWatch Logs: ~$0.50

## License

Internal Guild Education project
