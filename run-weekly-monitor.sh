#!/bin/bash
#
# Weekly AWS Resource Monitor
# Run this script weekly to scan dev and stage environments
#

set -e

# Configuration
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-YOUR_SLACK_WEBHOOK_URL_HERE}"
GOOGLE_CREDENTIALS="google-credentials.json"
DEV_PROFILE="guild-dev"
STAGE_PROFILE="guild-stage"
REGION="us-west-2"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=================================="
echo "AWS Resource Monitor - Weekly Run"
echo "=================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

# Check if required packages are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
python3 -c "import boto3, requests" 2>/dev/null || {
    echo -e "${RED}Missing required packages. Installing...${NC}"
    pip3 install -r requirements-monitor.txt
}

# Check AWS profiles
echo -e "${YELLOW}Checking AWS profiles...${NC}"
aws sts get-caller-identity --profile $DEV_PROFILE > /dev/null 2>&1 || {
    echo -e "${YELLOW}Dev profile expired. Logging in...${NC}"
    aws sso login --profile $DEV_PROFILE
}

aws sts get-caller-identity --profile $STAGE_PROFILE > /dev/null 2>&1 || {
    echo -e "${YELLOW}Stage profile expired. Logging in...${NC}"
    aws sso login --profile $STAGE_PROFILE
}

echo -e "${GREEN}✓ AWS profiles authenticated${NC}"
echo ""

# Check Slack webhook
if [ "$SLACK_WEBHOOK" == "YOUR_SLACK_WEBHOOK_URL_HERE" ]; then
    echo -e "${RED}Error: Please configure SLACK_WEBHOOK in this script${NC}"
    exit 1
fi

# Check Google credentials (optional)
GOOGLE_ARGS=""
if [ -f "$GOOGLE_CREDENTIALS" ]; then
    echo -e "${GREEN}✓ Google Drive credentials found${NC}"
    GOOGLE_ARGS="--google-credentials $GOOGLE_CREDENTIALS"
else
    echo -e "${YELLOW}⚠ Google Drive credentials not found. Skipping upload.${NC}"
fi

echo ""
echo "Starting resource scan..."
echo "This will take approximately 30-40 minutes for both environments."
echo ""

# Run the monitor
python3 aws_resource_monitor.py \
    --slack-webhook "$SLACK_WEBHOOK" \
    --dev-profile "$DEV_PROFILE" \
    --stage-profile "$STAGE_PROFILE" \
    --region "$REGION" \
    $GOOGLE_ARGS

echo ""
echo -e "${GREEN}=================================="
echo "Monitoring complete!"
echo "==================================${NC}"
