#!/bin/bash
# Quick start script for RDS Scanner

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}    AWS RDS Database Scanner${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
if [ ! -f "venv/installed" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
    touch venv/installed
fi

# Parse command line arguments
PROFILES="default"
REGIONS="us-east-1"
OUTPUT="rds_scan_results.csv"

while [[ $# -gt 0 ]]; do
    case $1 in
        --profiles)
            PROFILES="$2"
            shift 2
            ;;
        --regions)
            REGIONS="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./run.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --profiles  AWS profiles to scan (space-separated, default: default)"
            echo "  --regions   AWS regions to scan (space-separated, default: us-east-1)"
            echo "  --output    Output CSV file (default: rds_scan_results.csv)"
            echo "  --help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./run.sh"
            echo "  ./run.sh --profiles 'dev stage prod' --regions 'us-east-1 us-west-2'"
            echo "  ./run.sh --profiles 'prod' --regions 'us-east-1' --output prod_report.csv"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run the scanner
echo -e "${GREEN}Starting RDS scan...${NC}"
echo -e "${YELLOW}Profiles: ${PROFILES}${NC}"
echo -e "${YELLOW}Regions: ${REGIONS}${NC}"
echo -e "${YELLOW}Output: ${OUTPUT}${NC}"
echo ""

python3 rds_scanner.py --profiles $PROFILES --regions $REGIONS --output "$OUTPUT"

# Check if scan was successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Scan completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Results saved to: ${OUTPUT}${NC}"
    
    # Show preview of results
    if command -v head &> /dev/null && command -v column &> /dev/null; then
        echo ""
        echo -e "${YELLOW}Preview of results:${NC}"
        head -n 6 "$OUTPUT" | column -t -s,
        echo ""
    fi
else
    echo -e "${RED}Scan failed. Check the error messages above.${NC}"
    exit 1
fi
