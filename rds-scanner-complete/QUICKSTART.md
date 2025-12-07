# Quick Start Guide

Get up and running with the RDS Scanner in 5 minutes!

## Prerequisites

- AWS CLI configured with credentials
- Python 3.7+ installed
- Access to AWS RDS and CloudWatch

## Installation (2 minutes)

```bash
# 1. Install dependencies
pip install boto3

# 2. Configure AWS credentials (if not already done)
aws configure
```

## Run Your First Scan (3 minutes)

### Option 1: Using the convenience script (easiest)

```bash
chmod +x run.sh
./run.sh
```

### Option 2: Direct Python execution

```bash
python3 rds_scanner.py
```

### Option 3: Multi-environment scan

```bash
# Scan multiple AWS profiles and regions
python3 rds_scanner.py \
  --profiles dev stage prod \
  --regions us-east-1 us-west-2 \
  --output rds_report.csv
```

## View Results

Open the generated CSV file:
- `rds_scan_results.csv` - Main report with all databases
- `rds_scan_results.json` - JSON format for programmatic access

## What the Scanner Checks

✅ **Unused Databases** - Zero transactions in 6 months  
✅ **Underused Databases** - CPU < 50% OR < 50 transactions/month  
✅ **Tags** - Owner, Contact, Repo  

## Common Use Cases

### 1. Weekly Cost Optimization Report
```bash
# Run every Monday to identify cost savings opportunities
./run.sh --profiles prod --output weekly_report_$(date +%Y%m%d).csv
```

### 2. Multi-Account Audit
```bash
# Scan all environments
python3 rds_scanner.py \
  --profiles dev-account stage-account prod-account \
  --regions us-east-1 us-west-2 eu-west-1
```

### 3. Tag Compliance Check
```bash
# Find databases without proper tags
python3 rds_scanner.py --output tag_audit.csv
# Then filter CSV for "N/A" in owner/contact/repo columns
```

## Next Steps

- 📖 Read [README.md](README.md) for detailed documentation
- 🚀 Deploy to Lambda using [LAMBDA_DEPLOYMENT.md](LAMBDA_DEPLOYMENT.md)
- 🏗️ Use Terraform with [terraform_main.tf](terraform_main.tf)

## Troubleshooting

**Problem**: "No credentials found"  
**Solution**: Run `aws configure` to set up credentials

**Problem**: "Access Denied"  
**Solution**: Ensure your IAM user has the required permissions (see [iam_policy.json](iam_policy.json))

**Problem**: "No databases found"  
**Solution**: Check that you're scanning the correct regions and AWS profile

## Getting Help

- Check the detailed [README.md](README.md)
- Review the [iam_policy.json](iam_policy.json) for required permissions
- Enable debug logging by modifying the script

## Cost Savings Example

A typical organization can save **$500-5000/month** by:
- Deleting 5-10 unused databases
- Downsizing 10-20 underused databases
- Better resource allocation based on data

Start scanning now to find your savings opportunities! 🎯
