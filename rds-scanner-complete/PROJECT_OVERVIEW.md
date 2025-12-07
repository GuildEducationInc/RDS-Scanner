# AWS RDS Database Scanner - Project Overview

## 📋 What This Does

This automated solution scans your AWS RDS database instances across multiple environments (dev/stage/prod) and identifies:

1. **Unused Databases** - Zero transactions in the last 6 months
2. **Underused Databases** - CPU utilization < 50% OR transactions < 50/month
3. **Missing Tags** - Extracts owner, contact, and repo tags for accountability

## 🚀 Quick Start

1. Start here: [QUICKSTART.md](QUICKSTART.md)
2. Run: `./run.sh` or `python3 rds_scanner.py`
3. Review the generated `rds_scan_results.csv`

## 📁 Project Files

### Core Application
- **rds_scanner.py** - Main Python script for scanning RDS instances
- **requirements.txt** - Python dependencies (just boto3)
- **run.sh** - Convenience script for easy execution
- **iam_policy.json** - Required AWS IAM permissions

### Documentation
- **QUICKSTART.md** - Get started in 5 minutes ⚡
- **README.md** - Comprehensive documentation 📖
- **LAMBDA_DEPLOYMENT.md** - Serverless deployment guide 🔧

### Serverless Deployment
- **lambda_handler.py** - AWS Lambda function handler
- **terraform_main.tf** - Infrastructure as Code (Terraform)

### Configuration
- **config.example.json** - Example configuration file

## 💡 Usage Examples

### Local Execution
```bash
# Single environment
python3 rds_scanner.py

# Multiple environments
python3 rds_scanner.py --profiles dev stage prod --regions us-east-1 us-west-2
```

### Automated Execution (Lambda)
Deploy to AWS Lambda for scheduled weekly scans:
1. Follow [LAMBDA_DEPLOYMENT.md](LAMBDA_DEPLOYMENT.md)
2. Or use Terraform: `terraform apply` with terraform_main.tf

## 📊 Output Files

After running the scan, you'll get:

- **rds_scan_results.csv** - Spreadsheet with all findings
- **rds_scan_results.json** - JSON format for automation

Example CSV columns:
- Database identifier, engine, instance class
- Category (Unused/Underused/Active)
- CPU utilization, transaction counts
- Owner, contact, repo tags
- Reason for categorization

## 🎯 Use Cases

1. **Cost Optimization** - Identify databases to delete or downsize
2. **Tag Compliance** - Find untagged resources
3. **Resource Management** - Right-size your database fleet
4. **Security Audits** - Track database ownership
5. **FinOps** - Regular cost reporting to stakeholders

## 💰 Potential Savings

Organizations typically save:
- **Small teams**: $500-1,000/month
- **Medium companies**: $2,000-5,000/month
- **Large enterprises**: $10,000+/month

By identifying and removing just 5-10 unused databases!

## 🔧 Deployment Options

### Option 1: Local/Manual (Easiest)
Run the Python script on your laptop or server
- Setup time: 5 minutes
- Best for: Ad-hoc audits, testing

### Option 2: AWS Lambda (Recommended)
Serverless, scheduled execution
- Setup time: 30 minutes
- Best for: Automated weekly/monthly reports
- Cost: ~$1-2/month

### Option 3: Scheduled EC2/Container
Run in ECS, EKS, or EC2 with cron
- Setup time: 1-2 hours
- Best for: Existing container infrastructure

## 📋 Prerequisites

- AWS CLI configured
- Python 3.7+
- IAM permissions for RDS, CloudWatch, S3 (see iam_policy.json)
- Properly tagged RDS instances (Owner, Contact, Repo tags)

## 🛠️ Customization

The scanner is highly customizable:

1. **Thresholds**: Adjust CPU and transaction limits in code
2. **Time Periods**: Change from 6 months to any duration
3. **Metrics**: Add custom CloudWatch metrics
4. **Tags**: Modify which tags to extract
5. **Notifications**: Add Slack, email, or PagerDuty alerts

## 📞 Support

### Getting Started
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Check [README.md](README.md) for details
3. Review [iam_policy.json](iam_policy.json) for permissions

### Deployment
- Local: Run `./run.sh` or `python3 rds_scanner.py`
- Lambda: Follow [LAMBDA_DEPLOYMENT.md](LAMBDA_DEPLOYMENT.md)
- Terraform: Use terraform_main.tf with `terraform apply`

### Troubleshooting
- "No credentials": Run `aws configure`
- "Access Denied": Apply iam_policy.json to your user/role
- "No databases": Check regions and AWS profile

## 🔐 Security Notes

- Uses read-only AWS API calls
- No database credentials stored
- Does not connect to databases directly
- Only reads CloudWatch metrics and RDS metadata
- Safe to run in production accounts

## 📈 Next Steps

1. ✅ Run your first scan locally
2. ✅ Review and tag databases missing owner/contact
3. ✅ Delete or archive unused databases
4. ✅ Downsize underused databases
5. ✅ Set up automated Lambda scanning
6. ✅ Create monthly reports for stakeholders

## 🏆 Best Practices

1. **Run weekly** - Catch new unused databases quickly
2. **Tag everything** - Make accountability clear
3. **Document exceptions** - Some low-usage DBs are intentional (backups, DR)
4. **Act on findings** - Scanning without action wastes opportunity
5. **Track savings** - Measure cost reduction over time

---

**Ready to save money and optimize your database fleet?**

Start with: `./run.sh` or read [QUICKSTART.md](QUICKSTART.md)

For questions or issues, review the comprehensive [README.md](README.md)
