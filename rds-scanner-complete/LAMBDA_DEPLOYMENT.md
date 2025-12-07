# Lambda Deployment Guide

## Overview

Deploy the RDS Scanner as a serverless Lambda function that runs on a schedule (e.g., weekly) and sends reports to S3 and notifications via SNS.

## Architecture

```
CloudWatch Events (Cron) → Lambda Function → RDS API + CloudWatch API
                                 ↓
                            S3 Bucket (Reports)
                                 ↓
                            SNS Topic (Notifications)
```

## Prerequisites

- AWS CLI configured
- IAM permissions to create Lambda functions, S3 buckets, SNS topics, and IAM roles
- Python 3.9+ installed locally

## Step 1: Create S3 Bucket for Reports

```bash
aws s3 mb s3://your-rds-reports-bucket --region us-east-1
```

## Step 2: Create SNS Topic for Notifications

```bash
aws sns create-topic --name rds-scanner-alerts --region us-east-1

# Subscribe email address
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:rds-scanner-alerts \
  --protocol email \
  --notification-endpoint your-email@company.com
```

## Step 3: Create IAM Role for Lambda

Create a file `lambda-trust-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Create the role:

```bash
aws iam create-role \
  --role-name RDSScannerLambdaRole \
  --assume-role-policy-document file://lambda-trust-policy.json
```

Create a file `lambda-execution-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances",
        "rds:DescribeDBClusters",
        "rds:ListTagsForResource"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::your-rds-reports-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:*:*:rds-scanner-alerts"
    }
  ]
}
```

Attach the policy:

```bash
aws iam put-role-policy \
  --role-name RDSScannerLambdaRole \
  --policy-name RDSScannerExecutionPolicy \
  --policy-document file://lambda-execution-policy.json
```

## Step 4: Package the Lambda Function

Create a deployment package:

```bash
# Create a directory for the package
mkdir lambda_package
cd lambda_package

# Copy the scanner files
cp ../rds_scanner.py .
cp ../lambda_handler.py .

# Install dependencies
pip install boto3 -t .

# Create zip file
zip -r ../rds_scanner_lambda.zip .
cd ..
```

## Step 5: Create Lambda Function

```bash
aws lambda create-function \
  --function-name rds-database-scanner \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/RDSScannerLambdaRole \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://rds_scanner_lambda.zip \
  --timeout 900 \
  --memory-size 512 \
  --environment Variables="{
    REGIONS=us-east-1,us-west-2,
    S3_BUCKET=your-rds-reports-bucket,
    SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:rds-scanner-alerts,
    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
  }"
```

**Note**: For Slack integration setup, see [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md)

## Step 6: Create CloudWatch Event Rule (Schedule)

Run weekly on Mondays at 9 AM UTC:

```bash
aws events put-rule \
  --name rds-scanner-weekly \
  --schedule-expression "cron(0 9 ? * MON *)" \
  --description "Run RDS scanner weekly"

# Add permission for CloudWatch Events to invoke Lambda
aws lambda add-permission \
  --function-name rds-database-scanner \
  --statement-id rds-scanner-weekly-event \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-1:YOUR_ACCOUNT_ID:rule/rds-scanner-weekly

# Add Lambda as target
aws events put-targets \
  --rule rds-scanner-weekly \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:rds-database-scanner"
```

## Step 7: Test the Lambda Function

```bash
aws lambda invoke \
  --function-name rds-database-scanner \
  --log-type Tail \
  --query 'LogResult' \
  --output text \
  response.json | base64 --decode

cat response.json
```

## Update Lambda Function

If you make changes to the code:

```bash
# Repackage
cd lambda_package
zip -r ../rds_scanner_lambda.zip .
cd ..

# Update function
aws lambda update-function-code \
  --function-name rds-database-scanner \
  --zip-file fileb://rds_scanner_lambda.zip
```

## Update Environment Variables

```bash
aws lambda update-function-configuration \
  --function-name rds-database-scanner \
  --environment Variables="{
    REGIONS=us-east-1,us-west-2,eu-west-1,
    S3_BUCKET=your-rds-reports-bucket,
    SNS_TOPIC_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:rds-scanner-alerts,
    SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
  }"
```

**For Slack setup**: See [SLACK_INTEGRATION.md](SLACK_INTEGRATION.md) for complete guide

## Monitoring

View Lambda logs in CloudWatch:

```bash
aws logs tail /aws/lambda/rds-database-scanner --follow
```

## Cost Estimation

Assuming weekly execution:
- Lambda: ~$0.50/month (based on 900s execution time)
- CloudWatch API calls: Minimal (covered by free tier)
- RDS API calls: Free
- S3 storage: ~$0.02/month for reports
- SNS: ~$0.50/month for notifications

**Total: ~$1-2/month**

## Cleanup

```bash
# Delete CloudWatch Event Rule
aws events remove-targets --rule rds-scanner-weekly --ids 1
aws events delete-rule --name rds-scanner-weekly

# Delete Lambda function
aws lambda delete-function --function-name rds-database-scanner

# Delete IAM role
aws iam delete-role-policy --role-name RDSScannerLambdaRole --policy-name RDSScannerExecutionPolicy
aws iam delete-role --role-name RDSScannerLambdaRole

# Delete S3 bucket (after emptying it)
aws s3 rb s3://your-rds-reports-bucket --force

# Delete SNS topic
aws sns delete-topic --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:rds-scanner-alerts
```

## Terraform Deployment

See `terraform/` directory for Infrastructure as Code deployment.

## Troubleshooting

### Issue: Lambda times out
**Solution**: Increase timeout to 900 seconds (15 minutes) for large numbers of databases

### Issue: Not enough memory
**Solution**: Increase memory to 512 MB or 1024 MB

### Issue: Missing CloudWatch metrics
**Solution**: Ensure RDS instances have Enhanced Monitoring enabled
