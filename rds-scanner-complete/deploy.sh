#!/bin/bash
# CloudFormation Deployment Script for RDS Scanner

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   RDS Scanner - CloudFormation Deployment                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Configuration
STACK_NAME="rds-scanner"
TEMPLATE_FILE="rds-scanner-cloudformation.yaml"
PARAMETERS_FILE="parameters.json"
REGION="us-east-1"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: Template file '$TEMPLATE_FILE' not found${NC}"
    exit 1
fi

# Function to validate template
validate_template() {
    echo -e "${YELLOW}Validating CloudFormation template...${NC}"
    if aws cloudformation validate-template --template-body file://$TEMPLATE_FILE --region $REGION > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Template is valid${NC}"
    else
        echo -e "${RED}✗ Template validation failed${NC}"
        exit 1
    fi
}

# Function to check if stack exists
stack_exists() {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION > /dev/null 2>&1
}

# Function to prompt for Slack webhook
get_slack_webhook() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Slack Webhook Setup${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "To get your Slack webhook URL:"
    echo "1. Go to https://api.slack.com/messaging/webhooks"
    echo "2. Create a new webhook or use existing one"
    echo "3. Copy the webhook URL (starts with https://hooks.slack.com/)"
    echo ""
    
    read -p "Enter your Slack Webhook URL: " SLACK_WEBHOOK
    
    if [[ ! $SLACK_WEBHOOK =~ ^https://hooks\.slack\.com/services/ ]]; then
        echo -e "${RED}Warning: URL doesn't look like a valid Slack webhook${NC}"
        read -p "Continue anyway? (y/n): " confirm
        if [[ ! $confirm =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Function to get regions
get_regions() {
    echo ""
    echo -e "${YELLOW}Which AWS regions do you want to scan?${NC}"
    echo "Enter comma-separated regions (e.g., us-east-1,us-west-2,eu-west-1)"
    read -p "Regions [us-east-1]: " SCAN_REGIONS
    SCAN_REGIONS=${SCAN_REGIONS:-us-east-1}
}

# Function to create parameters file
create_parameters() {
    echo -e "${YELLOW}Creating parameters file...${NC}"
    
    cat > $PARAMETERS_FILE <<EOF
[
  {
    "ParameterKey": "SlackWebhookURL",
    "ParameterValue": "$SLACK_WEBHOOK"
  },
  {
    "ParameterKey": "ScanRegions",
    "ParameterValue": "$SCAN_REGIONS"
  },
  {
    "ParameterKey": "ProjectName",
    "ParameterValue": "rds-scanner"
  },
  {
    "ParameterKey": "LambdaTimeout",
    "ParameterValue": "900"
  },
  {
    "ParameterKey": "LambdaMemorySize",
    "ParameterValue": "512"
  },
  {
    "ParameterKey": "ReportRetentionDays",
    "ParameterValue": "90"
  },
  {
    "ParameterKey": "CPUThreshold",
    "ParameterValue": "50"
  },
  {
    "ParameterKey": "TransactionThreshold",
    "ParameterValue": "50"
  }
]
EOF
    
    echo -e "${GREEN}✓ Parameters file created${NC}"
}

# Function to deploy stack
deploy_stack() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Deploying CloudFormation Stack${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if stack_exists; then
        echo -e "${YELLOW}Stack already exists. Updating...${NC}"
        ACTION="update"
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            --parameters file://$PARAMETERS_FILE \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION
    else
        echo -e "${YELLOW}Creating new stack...${NC}"
        ACTION="create"
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            --parameters file://$PARAMETERS_FILE \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION
    fi
    
    echo -e "${GREEN}✓ Stack $ACTION initiated${NC}"
}

# Function to wait for stack completion
wait_for_stack() {
    echo ""
    echo -e "${YELLOW}Waiting for stack to complete (this may take 2-3 minutes)...${NC}"
    echo ""
    
    if [ "$ACTION" = "create" ]; then
        aws cloudformation wait stack-create-complete \
            --stack-name $STACK_NAME \
            --region $REGION && \
        echo -e "${GREEN}✓ Stack created successfully!${NC}" || \
        (echo -e "${RED}✗ Stack creation failed${NC}"; exit 1)
    else
        aws cloudformation wait stack-update-complete \
            --stack-name $STACK_NAME \
            --region $REGION && \
        echo -e "${GREEN}✓ Stack updated successfully!${NC}" || \
        (echo -e "${RED}✗ Stack update failed${NC}"; exit 1)
    fi
}

# Function to display outputs
display_outputs() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Get stack outputs
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs' \
        --output json)
    
    echo -e "${YELLOW}Stack Outputs:${NC}"
    echo "$OUTPUTS" | jq -r '.[] | "  \(.OutputKey): \(.OutputValue)"'
    
    echo ""
    echo -e "${GREEN}Next Steps:${NC}"
    echo "1. Test the Lambda function:"
    echo "   ${BLUE}aws lambda invoke --function-name rds-scanner-function --payload '{\"is_monday\": true}' response.json${NC}"
    echo ""
    echo "2. Check Slack for the test message"
    echo ""
    echo "3. View Lambda logs:"
    echo "   ${BLUE}aws logs tail /aws/lambda/rds-scanner-function --follow${NC}"
    echo ""
    echo "4. The scanner will run automatically:"
    echo "   - Every Monday at 9:00 AM UTC (with reminder)"
    echo "   - Every Friday at 9:00 AM UTC"
    echo ""
}

# Function to test deployment
test_deployment() {
    echo ""
    read -p "Would you like to test the Lambda function now? (y/n): " test_now
    
    if [[ $test_now =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${YELLOW}Testing Lambda function...${NC}"
        
        aws lambda invoke \
            --function-name rds-scanner-function \
            --payload '{"is_monday": true}' \
            --region $REGION \
            response.json > /dev/null 2>&1
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Lambda invoked successfully${NC}"
            echo ""
            echo "Response:"
            cat response.json | jq .
            echo ""
            echo -e "${GREEN}Check your Slack channel for the message!${NC}"
            rm response.json
        else
            echo -e "${RED}✗ Lambda invocation failed${NC}"
            echo "Check CloudWatch logs for details"
        fi
    fi
}

# Main execution
main() {
    # Validate template
    validate_template
    
    # Get user input
    get_slack_webhook
    get_regions
    
    # Create parameters
    create_parameters
    
    # Deploy stack
    deploy_stack
    
    # Wait for completion
    wait_for_stack
    
    # Display outputs
    display_outputs
    
    # Test deployment
    test_deployment
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Deployment Complete! Happy Scanning! 🎉                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
}

# Run main function
main
