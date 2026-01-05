#!/usr/bin/env python3
"""
Quick script to identify RDS instances in Extended Support
Extended Support applies to database versions past their standard support end date
Checks both RDS PostgreSQL and Aurora PostgreSQL instances

Current Extended Support Versions:
- PostgreSQL 11: Actively in Extended Support
- PostgreSQL 12: Actively in Extended Support
- PostgreSQL 13: Actively in Extended Support
"""

import boto3
import argparse
import csv
from datetime import datetime, timedelta
from decimal import Decimal

# Extended support cutoff dates for common database engines
# Versions older than these dates are typically in extended support
EXTENDED_SUPPORT_VERSIONS = {
    'postgres': {
        '11': '2023-11-09',  # PostgreSQL 11 standard support ended
        '12': '2024-11-14',  # PostgreSQL 12 standard support ended
        '13': '2025-11-13',  # PostgreSQL 13 standard support ended
    },
    'mysql': {
        '5.7': '2023-10-31',  # MySQL 5.7 standard support ended
    },
    'mariadb': {
        '10.3': '2023-05-25',  # MariaDB 10.3 standard support ended
        '10.4': '2024-06-18',  # MariaDB 10.4 standard support ended
        '10.5': '2025-06-24',  # MariaDB 10.5 standard support ended
    },
    'oracle-ee': {
        '19': '2024-04-30',  # Oracle 19c standard support (depends on license)
    }
}

# Upcoming extended support dates (versions that will enter extended support soon)
UPCOMING_EXTENDED_SUPPORT = {
    'postgres': {
        '14': '2026-11-12',  # PostgreSQL 14 standard support will end
    },
    'mysql': {
        '8.0': '2026-04-30',  # MySQL 8.0 standard support will end
    },
    'mariadb': {
        '10.6': '2026-07-06',  # MariaDB 10.6 standard support will end
    }
}

# RDS Extended Support Pricing (per vCPU-hour in us-west-2)
# Year 1: ~$0.10/vCPU-hour, Year 2+: ~$0.20/vCPU-hour
EXTENDED_SUPPORT_COST_YEAR1_PER_VCPU_HOUR = 0.10
EXTENDED_SUPPORT_COST_YEAR2_PER_VCPU_HOUR = 0.20

# Instance class to vCPU mapping for common RDS instance types
INSTANCE_VCPU_MAP = {
    # T3 instances
    'db.t3.micro': 2,
    'db.t3.small': 2,
    'db.t3.medium': 2,
    'db.t3.large': 2,
    'db.t3.xlarge': 4,
    'db.t3.2xlarge': 8,
    # T4g instances (Graviton2)
    'db.t4g.micro': 2,
    'db.t4g.small': 2,
    'db.t4g.medium': 2,
    'db.t4g.large': 2,
    'db.t4g.xlarge': 4,
    'db.t4g.2xlarge': 8,
    # M5 instances
    'db.m5.large': 2,
    'db.m5.xlarge': 4,
    'db.m5.2xlarge': 8,
    'db.m5.4xlarge': 16,
    'db.m5.8xlarge': 32,
    'db.m5.12xlarge': 48,
    'db.m5.16xlarge': 64,
    'db.m5.24xlarge': 96,
    # M6g instances (Graviton2)
    'db.m6g.large': 2,
    'db.m6g.xlarge': 4,
    'db.m6g.2xlarge': 8,
    'db.m6g.4xlarge': 16,
    'db.m6g.8xlarge': 32,
    'db.m6g.12xlarge': 48,
    'db.m6g.16xlarge': 64,
    # R4 instances
    'db.r4.large': 2,
    'db.r4.xlarge': 4,
    'db.r4.2xlarge': 8,
    'db.r4.4xlarge': 16,
    'db.r4.8xlarge': 32,
    'db.r4.16xlarge': 64,
    # R5 instances
    'db.r5.large': 2,
    'db.r5.xlarge': 4,
    'db.r5.2xlarge': 8,
    'db.r5.4xlarge': 16,
    'db.r5.8xlarge': 32,
    'db.r5.12xlarge': 48,
    'db.r5.16xlarge': 64,
    'db.r5.24xlarge': 96,
    # R7g instances (Graviton3)
    'db.r7g.large': 2,
    'db.r7g.xlarge': 4,
    'db.r7g.2xlarge': 8,
    'db.r7g.4xlarge': 16,
    'db.r7g.8xlarge': 32,
    'db.r7g.12xlarge': 48,
    'db.r7g.16xlarge': 64,
    # Serverless - estimated average at 2 ACUs (1 ACU = 2 GB RAM, ~0.5 vCPU equivalent)
    'db.serverless': 1,  # Conservative estimate for serverless
}

def check_extended_support(engine, version):
    """Check if a given engine version is likely in extended support"""
    engine_base = engine.split('-')[0]  # Handle oracle-ee, oracle-se2, etc.

    # Map aurora to postgres for version checking
    if engine == 'aurora-postgresql':
        engine_base = 'postgres'

    if engine_base not in EXTENDED_SUPPORT_VERSIONS:
        return False, "Unknown"

    # Extract major version
    version_parts = version.split('.')
    if engine_base == 'postgres':
        major_version = version_parts[0]
    elif engine_base in ['mysql', 'mariadb']:
        major_version = f"{version_parts[0]}.{version_parts[1]}"
    elif engine_base == 'oracle':
        major_version = version_parts[0]
    else:
        return False, "Unknown"

    if major_version in EXTENDED_SUPPORT_VERSIONS[engine_base]:
        return True, EXTENDED_SUPPORT_VERSIONS[engine_base][major_version]

    return False, "Standard Support"

def check_upcoming_extended_support(engine, version):
    """Check if a given engine version will enter extended support within 30 days"""
    engine_base = engine.split('-')[0]  # Handle oracle-ee, oracle-se2, etc.

    # Map aurora to postgres for version checking
    if engine == 'aurora-postgresql':
        engine_base = 'postgres'

    if engine_base not in UPCOMING_EXTENDED_SUPPORT:
        return False, None

    # Extract major version
    version_parts = version.split('.')
    if engine_base == 'postgres':
        major_version = version_parts[0]
    elif engine_base in ['mysql', 'mariadb']:
        major_version = f"{version_parts[0]}.{version_parts[1]}"
    elif engine_base == 'oracle':
        major_version = version_parts[0]
    else:
        return False, None

    if major_version in UPCOMING_EXTENDED_SUPPORT[engine_base]:
        support_end_date_str = UPCOMING_EXTENDED_SUPPORT[engine_base][major_version]
        support_end_date = datetime.strptime(support_end_date_str, '%Y-%m-%d')
        today = datetime.now()
        days_until_end = (support_end_date - today).days

        # Check if support ends within 30 days
        if 0 <= days_until_end <= 30:
            return True, support_end_date_str

    return False, None

def calculate_extended_support_cost(instance_class, support_end_date_str):
    """Calculate estimated monthly extended support cost"""
    # Get vCPU count
    vcpu_count = INSTANCE_VCPU_MAP.get(instance_class, 2)  # Default to 2 if unknown

    # Parse support end date
    try:
        support_end_date = datetime.strptime(support_end_date_str, '%Y-%m-%d')
    except:
        return 0.0, 0, "Unknown"

    # Calculate which year of extended support we're in
    today = datetime.now()
    days_in_extended_support = (today - support_end_date).days
    years_in_extended_support = days_in_extended_support / 365.25

    # Determine cost per vCPU-hour based on year
    if years_in_extended_support < 1:
        cost_per_vcpu_hour = EXTENDED_SUPPORT_COST_YEAR1_PER_VCPU_HOUR
        support_year = "Year 1"
    else:
        cost_per_vcpu_hour = EXTENDED_SUPPORT_COST_YEAR2_PER_VCPU_HOUR
        support_year = f"Year {int(years_in_extended_support) + 1}"

    # Calculate monthly cost (730 hours per month average)
    hours_per_month = 730
    monthly_cost = vcpu_count * cost_per_vcpu_hour * hours_per_month

    return monthly_cost, vcpu_count, support_year

def scan_rds_instances(profile_name, environment_name):
    """Scan RDS instances in an environment"""
    session = boto3.Session(profile_name=profile_name)
    rds_client = session.client('rds', region_name='us-west-2')

    print(f"\n{'='*80}")
    print(f"Scanning {environment_name.upper()} environment (Profile: {profile_name})")
    print(f"{'='*80}")

    # Get account ID
    sts = session.client('sts')
    account_id = sts.get_caller_identity()['Account']
    print(f"Account ID: {account_id}")

    extended_support_instances = []
    upcoming_extended_instances = []
    all_instances = []

    # Paginate through all RDS instances
    paginator = rds_client.get_paginator('describe_db_instances')

    for page in paginator.paginate():
        for instance in page['DBInstances']:
            db_id = instance['DBInstanceIdentifier']
            engine = instance['Engine']
            version = instance['EngineVersion']
            instance_class = instance['DBInstanceClass']
            status = instance['DBInstanceStatus']

            is_extended, support_date = check_extended_support(engine, version)
            is_upcoming, upcoming_date = check_upcoming_extended_support(engine, version)

            # Calculate extended support cost if applicable
            monthly_cost = 0.0
            vcpu_count = 0
            support_year = "N/A"

            if is_extended and support_date != "Unknown":
                monthly_cost, vcpu_count, support_year = calculate_extended_support_cost(instance_class, support_date)

            instance_info = {
                'identifier': db_id,
                'engine': engine,
                'version': version,
                'class': instance_class,
                'status': status,
                'extended_support': is_extended,
                'support_date': support_date,
                'upcoming_extended': is_upcoming,
                'upcoming_date': upcoming_date,
                'monthly_cost': monthly_cost,
                'vcpu_count': vcpu_count,
                'support_year': support_year
            }

            all_instances.append(instance_info)

            if is_extended:
                extended_support_instances.append(instance_info)
            elif is_upcoming:
                upcoming_extended_instances.append(instance_info)

    # Calculate total monthly cost
    total_monthly_cost = sum(inst['monthly_cost'] for inst in extended_support_instances)

    # Print summary
    print(f"\nTotal RDS Instances: {len(all_instances)}")
    print(f"Extended Support Instances: {len(extended_support_instances)}")
    print(f"Upcoming Extended Support Instances (within 30 days): {len(upcoming_extended_instances)}")
    print(f"Estimated Monthly Extended Support Cost: ${total_monthly_cost:,.2f}")

    if extended_support_instances:
        print(f"\n{'='*80}")
        print(f"RDS INSTANCES IN EXTENDED SUPPORT - {environment_name.upper()}")
        print(f"{'='*80}")
        print(f"{'Instance ID':<50} {'Engine':<15} {'Version':<12} {'Class':<20}")
        print(f"{'-'*50} {'-'*15} {'-'*12} {'-'*20}")

        for inst in extended_support_instances:
            print(f"{inst['identifier']:<50} {inst['engine']:<15} {inst['version']:<12} {inst['class']:<20}")
    else:
        print(f"\n✓ No instances in extended support found in {environment_name.upper()}")

    if upcoming_extended_instances:
        print(f"\n{'='*80}")
        print(f"RDS INSTANCES ENTERING EXTENDED SUPPORT SOON - {environment_name.upper()}")
        print(f"{'='*80}")
        print(f"{'Instance ID':<50} {'Engine':<15} {'Version':<12} {'Class':<20}")
        print(f"{'-'*50} {'-'*15} {'-'*12} {'-'*20}")

        for inst in upcoming_extended_instances:
            print(f"{inst['identifier']:<50} {inst['engine']:<15} {inst['version']:<12} {inst['class']:<20}")

    return extended_support_instances, upcoming_extended_instances, all_instances

def main():
    parser = argparse.ArgumentParser(description='Check RDS instances in Extended Support')
    parser.add_argument('--dev-profile', default='guild-dev', help='AWS profile for dev')
    parser.add_argument('--stage-profile', default='guild-stage', help='AWS profile for stage')
    parser.add_argument('--prod-profile', default='guild-prod', help='AWS profile for prod')

    args = parser.parse_args()

    print("="*80)
    print("RDS Extended Support Check")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    all_extended = []
    all_upcoming = []

    # Scan DEV
    try:
        dev_extended, dev_upcoming, dev_all = scan_rds_instances(args.dev_profile, 'dev')
        all_extended.extend([('dev', inst) for inst in dev_extended])
        all_upcoming.extend([('dev', inst) for inst in dev_upcoming])
    except Exception as e:
        print(f"\n✗ Error scanning DEV: {e}")

    # Scan STAGE
    try:
        stage_extended, stage_upcoming, stage_all = scan_rds_instances(args.stage_profile, 'stage')
        all_extended.extend([('stage', inst) for inst in stage_extended])
        all_upcoming.extend([('stage', inst) for inst in stage_upcoming])
    except Exception as e:
        print(f"\n✗ Error scanning STAGE: {e}")

    # Scan PROD
    try:
        prod_extended, prod_upcoming, prod_all = scan_rds_instances(args.prod_profile, 'prod')
        all_extended.extend([('prod', inst) for inst in prod_extended])
        all_upcoming.extend([('prod', inst) for inst in prod_upcoming])
    except Exception as e:
        print(f"\n✗ Error scanning PROD: {e}")

    # Calculate total costs across all environments
    total_monthly_cost_all = sum(inst['monthly_cost'] for env, inst in all_extended)
    total_annual_cost_all = total_monthly_cost_all * 12

    # Final summary
    print(f"\n{'='*80}")
    print("SUMMARY - ALL ENVIRONMENTS")
    print(f"{'='*80}")
    print(f"Total Extended Support Instances: {len(all_extended)}")
    print(f"Total Upcoming Extended Support Instances (within 30 days): {len(all_upcoming)}")
    print(f"\nEstimated Extended Support Costs:")
    print(f"  Monthly: ${total_monthly_cost_all:,.2f}")
    print(f"  Annual:  ${total_annual_cost_all:,.2f}")

    if all_extended:
        print(f"\n*** CURRENTLY IN EXTENDED SUPPORT ***")
        print(f"{'Environment':<12} {'Instance ID':<50} {'Engine':<15} {'Version':<12}")
        print(f"{'-'*12} {'-'*50} {'-'*15} {'-'*12}")
        for env, inst in all_extended:
            print(f"{env.upper():<12} {inst['identifier']:<50} {inst['engine']:<15} {inst['version']:<12}")

    if all_upcoming:
        print(f"\n*** ENTERING EXTENDED SUPPORT SOON (within 30 days) ***")
        print(f"{'Environment':<12} {'Instance ID':<50} {'Engine':<15} {'Version':<12}")
        print(f"{'-'*12} {'-'*50} {'-'*15} {'-'*12}")
        for env, inst in all_upcoming:
            print(f"{env.upper():<12} {inst['identifier']:<50} {inst['engine']:<15} {inst['version']:<12}")

    # Generate CSV report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"rds_extended_support_{timestamp}.csv"

    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(['Report Type', 'RDS Extended Support Check'])
        writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['Total Extended Support Instances', len(all_extended)])
        writer.writerow(['Total Upcoming Extended Support Instances (within 30 days)', len(all_upcoming)])
        writer.writerow(['Estimated Monthly Cost', f'${total_monthly_cost_all:,.2f}'])
        writer.writerow(['Estimated Annual Cost', f'${total_annual_cost_all:,.2f}'])
        writer.writerow([])

        # Write data header
        writer.writerow(['Environment', 'Instance ID', 'Engine', 'Version', 'Instance Class', 'vCPUs', 'Instance Status', 'Support Status', 'Support End Date', 'Support Year', 'Monthly Cost (USD)'])

        # Write currently in extended support
        for env, inst in all_extended:
            writer.writerow([
                env.upper(),
                inst['identifier'],
                inst['engine'],
                inst['version'],
                inst['class'],
                inst['vcpu_count'],
                inst['status'],
                'In Extended Support',
                inst['support_date'],
                inst['support_year'],
                f'${inst["monthly_cost"]:.2f}'
            ])

        # Write upcoming extended support instances
        for env, inst in all_upcoming:
            writer.writerow([
                env.upper(),
                inst['identifier'],
                inst['engine'],
                inst['version'],
                inst['class'],
                inst.get('vcpu_count', 0),
                inst['status'],
                'Entering Extended Support Soon',
                inst['upcoming_date'],
                'N/A',
                '$0.00'
            ])

    print(f"\n✓ CSV report saved: {csv_filename}")

    print("\n" + "="*80)
    print("Extended Support Versions Checked:")
    print("- PostgreSQL 11 (RDS & Aurora): In Extended Support")
    print("- PostgreSQL 12 (RDS & Aurora): In Extended Support")
    print("- PostgreSQL 13 (RDS & Aurora): In Extended Support")
    print("\nCost Calculation Notes:")
    print("- Year 1 Extended Support: $0.10/vCPU-hour")
    print("- Year 2+ Extended Support: $0.20/vCPU-hour")
    print("- Serverless instances estimated at 1 vCPU (conservative)")
    print("- Actual costs may vary based on actual usage and AWS pricing")
    print("\nFor accurate billing, verify with AWS Cost Explorer or your AWS bill.")
    print("="*80)

if __name__ == '__main__':
    main()
