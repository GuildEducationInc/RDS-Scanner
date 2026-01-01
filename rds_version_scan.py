#!/usr/bin/env python3
"""
Script to identify RDS instances with engine versions less than 15
"""

import boto3
import argparse
import csv
from datetime import datetime

def get_major_version(engine, version):
    """Extract the major version number from engine version string"""
    try:
        version_parts = version.split('.')
        engine_base = engine.split('-')[0]

        if engine_base == 'postgres':
            # PostgreSQL uses first number as major version (e.g., 12.22 -> 12)
            return int(version_parts[0])
        elif engine_base in ['mysql', 'mariadb']:
            # MySQL/MariaDB uses first two numbers (e.g., 5.7.44 -> 5.7, but we take first for < 15 check)
            return int(version_parts[0])
        elif engine_base == 'oracle':
            # Oracle uses first number (e.g., 19.0.0.0 -> 19)
            return int(version_parts[0])
        elif engine_base == 'sqlserver':
            # SQL Server major version
            return int(version_parts[0])
        else:
            # For other engines, try to parse first number
            return int(version_parts[0])
    except (ValueError, IndexError):
        return None

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

    instances_below_v15 = []
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

            major_version = get_major_version(engine, version)

            instance_info = {
                'identifier': db_id,
                'engine': engine,
                'version': version,
                'major_version': major_version,
                'class': instance_class,
                'status': status
            }

            all_instances.append(instance_info)

            # Check if major version is less than 15
            if major_version is not None and major_version < 15:
                instances_below_v15.append(instance_info)

    # Print summary
    print(f"\nTotal RDS Instances: {len(all_instances)}")
    print(f"Instances with version < 15: {len(instances_below_v15)}")

    if instances_below_v15:
        print(f"\n{'='*80}")
        print(f"RDS INSTANCES WITH VERSION < 15 - {environment_name.upper()}")
        print(f"{'='*80}")
        print(f"{'Instance ID':<50} {'Engine':<15} {'Version':<15} {'Major':<8} {'Class':<20}")
        print(f"{'-'*50} {'-'*15} {'-'*15} {'-'*8} {'-'*20}")

        # Sort by major version, then by engine
        instances_below_v15.sort(key=lambda x: (x['major_version'], x['engine'], x['identifier']))

        for inst in instances_below_v15:
            print(f"{inst['identifier']:<50} {inst['engine']:<15} {inst['version']:<15} {inst['major_version']:<8} {inst['class']:<20}")
    else:
        print(f"\n✓ No instances with version < 15 found in {environment_name.upper()}")

    return instances_below_v15, all_instances

def main():
    parser = argparse.ArgumentParser(description='Check RDS instances with version < 15')
    parser.add_argument('--dev-profile', default='guild-dev', help='AWS profile for dev')
    parser.add_argument('--stage-profile', default='guild-stage', help='AWS profile for stage')
    parser.add_argument('--prod-profile', default='guild-prod', help='AWS profile for prod')

    args = parser.parse_args()

    print("="*80)
    print("RDS Version Scanner - Instances with Version < 15")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    all_instances_v15 = []

    # Scan DEV
    try:
        dev_instances, dev_all = scan_rds_instances(args.dev_profile, 'dev')
        all_instances_v15.extend([('dev', inst) for inst in dev_instances])
    except Exception as e:
        print(f"\n✗ Error scanning DEV: {e}")

    # Scan STAGE
    try:
        stage_instances, stage_all = scan_rds_instances(args.stage_profile, 'stage')
        all_instances_v15.extend([('stage', inst) for inst in stage_instances])
    except Exception as e:
        print(f"\n✗ Error scanning STAGE: {e}")

    # Scan PROD
    try:
        prod_instances, prod_all = scan_rds_instances(args.prod_profile, 'prod')
        all_instances_v15.extend([('prod', inst) for inst in prod_instances])
    except Exception as e:
        print(f"\n✗ Error scanning PROD: {e}")

    # Final summary
    print(f"\n{'='*80}")
    print("SUMMARY - ALL ENVIRONMENTS")
    print(f"{'='*80}")
    print(f"Total Instances with Version < 15: {len(all_instances_v15)}")

    if all_instances_v15:
        print(f"\n{'Environment':<12} {'Instance ID':<50} {'Engine':<15} {'Version':<15} {'Major':<8}")
        print(f"{'-'*12} {'-'*50} {'-'*15} {'-'*15} {'-'*8}")

        # Sort by major version
        all_instances_v15.sort(key=lambda x: (x[1]['major_version'], x[1]['engine'], x[1]['identifier']))

        for env, inst in all_instances_v15:
            print(f"{env.upper():<12} {inst['identifier']:<50} {inst['engine']:<15} {inst['version']:<15} {inst['major_version']:<8}")

    # Generate CSV report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"rds_version_below_15_{timestamp}.csv"

    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header
        writer.writerow(['Report Type', 'RDS Instances with Version < 15'])
        writer.writerow(['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow(['Total Instances', len(all_instances_v15)])
        writer.writerow([])

        # Write data header
        writer.writerow(['Environment', 'Instance ID', 'Engine', 'Version', 'Major Version', 'Instance Class', 'Status'])

        # Write data rows
        for env, inst in all_instances_v15:
            writer.writerow([
                env.upper(),
                inst['identifier'],
                inst['engine'],
                inst['version'],
                inst['major_version'],
                inst['class'],
                inst['status']
            ])

    print(f"\n✓ CSV report saved: {csv_filename}")

    print("\n" + "="*80)
    print("Note: Major version extracted based on database engine type.")
    print("For PostgreSQL: 11.x, 12.x, 13.x, 14.x are all < 15")
    print("For MySQL: 5.x, 8.x are all < 15")
    print("="*80)

if __name__ == '__main__':
    main()
