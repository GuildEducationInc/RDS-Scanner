# Terraform Configuration for RDS Scanner Lambda
# Deploy with: terraform init && terraform apply

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "scan_regions" {
  description = "Comma-separated list of regions to scan"
  type        = string
  default     = "us-east-1,us-west-2"
}

variable "schedule_expression" {
  description = "CloudWatch Events schedule expression"
  type        = string
  default     = "cron(0 9 ? * MON *)" # Every Monday at 9 AM UTC
}

variable "email_address" {
  description = "Email address for SNS notifications"
  type        = string
}

variable "slack_webhook_url" {
  description = "Slack webhook URL for notifications"
  type        = string
  default     = ""
  sensitive   = true
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "rds-scanner"
}

# S3 Bucket for Reports
resource "aws_s3_bucket" "reports" {
  bucket = "${var.project_name}-reports-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "RDS Scanner Reports"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "reports" {
  bucket = aws_s3_bucket.reports.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "delete-old-reports"
    status = "Enabled"

    expiration {
      days = 90 # Keep reports for 90 days
    }
  }
}

# SNS Topic for Notifications
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"

  tags = {
    Name        = "RDS Scanner Alerts"
    ManagedBy   = "Terraform"
  }
}

resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.email_address
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "RDS Scanner Lambda Role"
    ManagedBy   = "Terraform"
  }
}

# IAM Policy for Lambda
resource "aws_iam_role_policy" "lambda" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:ListTagsForResource"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl"
        ]
        Resource = "${aws_s3_bucket.reports.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish"
        ]
        Resource = aws_sns_topic.alerts.arn
      }
    ]
  })
}

# Lambda Function
data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "${path.module}/../lambda_package"
  output_path = "${path.module}/rds_scanner_lambda.zip"
}

resource "aws_lambda_function" "scanner" {
  filename         = data.archive_file.lambda.output_path
  function_name    = "${var.project_name}-function"
  role            = aws_iam_role.lambda.arn
  handler         = "lambda_handler.lambda_handler"
  source_code_hash = data.archive_file.lambda.output_base64sha256
  runtime         = "python3.9"
  timeout         = 900
  memory_size     = 512

  environment {
    variables = {
      REGIONS           = var.scan_regions
      S3_BUCKET         = aws_s3_bucket.reports.id
      SNS_TOPIC_ARN     = aws_sns_topic.alerts.arn
      SLACK_WEBHOOK_URL = var.slack_webhook_url
    }
  }

  tags = {
    Name        = "RDS Scanner"
    ManagedBy   = "Terraform"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.scanner.function_name}"
  retention_in_days = 30

  tags = {
    Name        = "RDS Scanner Logs"
    ManagedBy   = "Terraform"
  }
}

# CloudWatch Event Rule (Schedule)
resource "aws_cloudwatch_event_rule" "schedule" {
  name                = "${var.project_name}-schedule"
  description         = "Trigger RDS scanner on schedule"
  schedule_expression = var.schedule_expression

  tags = {
    Name        = "RDS Scanner Schedule"
    ManagedBy   = "Terraform"
  }
}

resource "aws_cloudwatch_event_target" "lambda" {
  rule      = aws_cloudwatch_event_rule.schedule.name
  target_id = "RDSScanner"
  arn       = aws_lambda_function.scanner.arn
}

resource "aws_lambda_permission" "cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scanner.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.schedule.arn
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# Outputs
output "s3_bucket_name" {
  description = "S3 bucket for reports"
  value       = aws_s3_bucket.reports.id
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = aws_sns_topic.alerts.arn
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.scanner.function_name
}

output "lambda_function_arn" {
  description = "Lambda function ARN"
  value       = aws_lambda_function.scanner.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for Lambda"
  value       = aws_cloudwatch_log_group.lambda.name
}
