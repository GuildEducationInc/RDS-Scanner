#!/usr/bin/env python3
"""
AWS RDS Database Scanner
Scans RDS instances across multiple AWS accounts/environments to identify:
- Unused databases (zero transactions in last 6 months)
- Underused databases (CPU < 50% OR transactions < 50/month)
- Extracts tags (owner, contact, repo)
"""

import boto3
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse
import json


class RDSScanner:
    def __init__(self, region: str = 'us-east-1', profile: str = None):
        """Initialize AWS clients"""
        session = boto3.Session(profile_name=profile, region_name=region)
        self.rds_client = session.client('rds')
        self.cloudwatch_client = session.client('cloudwatch')
        self.region = region
        self.profile = profile or 'default'
        
    def get_all_db_instances(self) -> List[Dict[str, Any]]:
        """Retrieve all RDS database instances"""
        instances = []
        try:
            paginator = self.rds_client.get_paginator('describe_db_instances')
            for page in paginator.paginate():
                instances.extend(page['DBInstances'])
        except Exception as e:
            print(f"Error retrieving DB instances: {e}")
        return instances
    
    def get_cloudwatch_metric(self, db_instance_id: str, metric_name: str, 
                             start_time: datetime, end_time: datetime, 
                             statistic: str = 'Average') -> float:
        """Get CloudWatch metric for a database instance"""
        try:
            response = self.cloudwatch_client.get_metric_statistics(
                Namespace='AWS/RDS',
                MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': 'DBInstanceIdentifier',
                        'Value': db_instance_id
                    }
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # 1 day
                Statistics=[statistic]
            )
            
            if response['Datapoints']:
                # Return average of all datapoints
                values = [dp[statistic] for dp in response['Datapoints']]
                return sum(values) / len(values) if values else 0.0
            return 0.0
        except Exception as e:
            print(f"Error getting metric {metric_name} for {db_instance_id}: {e}")
            return 0.0
    
    def get_transaction_count(self, db_instance_id: str, engine: str, 
                            start_time: datetime, end_time: datetime) -> float:
        """Get total transaction count based on database engine"""
        # Different engines have different metrics
        transaction_metrics = {
            'postgres': 'DatabaseConnections',
            'mysql': 'DatabaseConnections',
            'aurora-mysql': 'DatabaseConnections',
            'aurora-postgresql': 'DatabaseConnections',
            'mariadb': 'DatabaseConnections',
            'oracle': 'DatabaseConnections',
            'sqlserver': 'DatabaseConnections'
        }
        
        # Try to get read/write IOPS as a proxy for transactions
        read_iops = self.get_cloudwatch_metric(
            db_instance_id, 'ReadIOPS', start_time, end_time, 'Sum'
        )
        write_iops = self.get_cloudwatch_metric(
            db_instance_id, 'WriteIOPS', start_time, end_time, 'Sum'
        )
        
        # Total IOPS is a good proxy for database activity
        return read_iops + write_iops
    
    def get_cpu_utilization(self, db_instance_id: str, 
                           start_time: datetime, end_time: datetime) -> float:
        """Get average CPU utilization"""
        return self.get_cloudwatch_metric(
            db_instance_id, 'CPUUtilization', start_time, end_time, 'Average'
        )
    
    def get_db_tags(self, db_arn: str) -> Dict[str, str]:
        """Extract specific tags from database instance"""
        try:
            response = self.rds_client.list_tags_for_resource(ResourceName=db_arn)
            tags = {tag['Key']: tag['Value'] for tag in response['TagList']}
            return {
                'owner': tags.get('Owner', tags.get('owner', 'N/A')),
                'contact': tags.get('Contact', tags.get('contact', 'N/A')),
                'repo': tags.get('Repo', tags.get('repo', tags.get('Repository', 'N/A'))),
                'environment': tags.get('Environment', tags.get('environment', 'N/A'))
            }
        except Exception as e:
            print(f"Error getting tags for {db_arn}: {e}")
            return {'owner': 'N/A', 'contact': 'N/A', 'repo': 'N/A', 'environment': 'N/A'}
    
    def categorize_database(self, db_instance: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and categorize a database instance"""
        db_id = db_instance['DBInstanceIdentifier']
        db_arn = db_instance['DBInstanceArn']
        engine = db_instance['Engine']
        instance_class = db_instance['DBInstanceClass']
        status = db_instance['DBInstanceStatus']
        
        # Time ranges
        end_time = datetime.utcnow()
        six_months_ago = end_time - timedelta(days=180)
        one_month_ago = end_time - timedelta(days=30)
        
        print(f"Analyzing: {db_id} ({engine})...")
        
        # Get metrics
        cpu_6_months = self.get_cpu_utilization(db_id, six_months_ago, end_time)
        transactions_6_months = self.get_transaction_count(db_id, engine, six_months_ago, end_time)
        transactions_1_month = self.get_transaction_count(db_id, engine, one_month_ago, end_time)
        
        # Get tags
        tags = self.get_db_tags(db_arn)
        
        # Categorize
        category = 'Active'
        reason = ''
        
        if transactions_6_months == 0:
            category = 'Unused'
            reason = 'Zero transactions in last 6 months'
        elif cpu_6_months < 50 or transactions_1_month < 50:
            category = 'Underused'
            reasons = []
            if cpu_6_months < 50:
                reasons.append(f'CPU: {cpu_6_months:.2f}%')
            if transactions_1_month < 50:
                reasons.append(f'Transactions/month: {transactions_1_month:.0f}')
            reason = '; '.join(reasons)
        
        return {
            'db_identifier': db_id,
            'db_arn': db_arn,
            'engine': engine,
            'instance_class': instance_class,
            'status': status,
            'region': self.region,
            'profile': self.profile,
            'category': category,
            'reason': reason,
            'cpu_utilization_6mo': f'{cpu_6_months:.2f}%',
            'transactions_6mo': f'{transactions_6_months:.0f}',
            'transactions_1mo': f'{transactions_1_month:.0f}',
            'owner': tags['owner'],
            'contact': tags['contact'],
            'repo': tags['repo'],
            'environment': tags['environment']
        }
    
    def scan_databases(self) -> List[Dict[str, Any]]:
        """Scan all databases and return analysis"""
        print(f"\n{'='*80}")
        print(f"Scanning RDS instances in region: {self.region}, profile: {self.profile}")
        print(f"{'='*80}\n")
        
        instances = self.get_all_db_instances()
        print(f"Found {len(instances)} database instances\n")
        
        results = []
        for instance in instances:
            result = self.categorize_database(instance)
            results.append(result)
        
        return results


def export_to_csv(results: List[Dict[str, Any]], filename: str):
    """Export results to CSV file"""
    if not results:
        print("No results to export")
        return
    
    fieldnames = [
        'db_identifier', 'engine', 'instance_class', 'status', 'region', 'profile',
        'category', 'reason', 'cpu_utilization_6mo', 'transactions_6mo', 
        'transactions_1mo', 'owner', 'contact', 'repo', 'environment'
    ]
    
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            # Filter out db_arn for CSV
            row = {k: v for k, v in result.items() if k in fieldnames}
            writer.writerow(row)
    
    print(f"\n{'='*80}")
    print(f"Results exported to: {filename}")
    print(f"{'='*80}")


def export_to_json(results: List[Dict[str, Any]], filename: str):
    """Export results to JSON file"""
    with open(filename, 'w') as jsonfile:
        json.dump(results, jsonfile, indent=2)
    print(f"Results also exported to: {filename}")


def print_summary(results: List[Dict[str, Any]]):
    """Print summary statistics"""
    unused = [r for r in results if r['category'] == 'Unused']
    underused = [r for r in results if r['category'] == 'Underused']
    active = [r for r in results if r['category'] == 'Active']
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Total databases scanned: {len(results)}")
    print(f"  - Unused (0 transactions in 6 months): {len(unused)}")
    print(f"  - Underused (CPU < 50% OR transactions < 50/month): {len(underused)}")
    print(f"  - Active: {len(active)}")
    
    if unused:
        print(f"\nUnused databases:")
        for db in unused:
            print(f"  - {db['db_identifier']} ({db['engine']}) - Owner: {db['owner']}")
    
    if underused:
        print(f"\nUnderused databases:")
        for db in underused:
            print(f"  - {db['db_identifier']} ({db['engine']}) - {db['reason']} - Owner: {db['owner']}")


def main():
    parser = argparse.ArgumentParser(
        description='Scan AWS RDS instances to identify unused and underused databases'
    )
    parser.add_argument(
        '--profiles',
        nargs='+',
        help='AWS profile names (e.g., dev stage prod)',
        default=['default']
    )
    parser.add_argument(
        '--regions',
        nargs='+',
        help='AWS regions to scan (e.g., us-east-1 us-west-2)',
        default=['us-east-1']
    )
    parser.add_argument(
        '--output',
        help='Output CSV filename',
        default='rds_scan_results.csv'
    )
    parser.add_argument(
        '--json-output',
        help='Output JSON filename',
        default='rds_scan_results.json'
    )
    parser.add_argument(
        '--slack-webhook',
        help='Slack webhook URL for notifications',
        default=None
    )
    parser.add_argument(
        '--s3-url',
        help='S3 URL for report (included in Slack message)',
        default=None
    )
    
    args = parser.parse_args()
    
    all_results = []
    
    for profile in args.profiles:
        for region in args.regions:
            try:
                scanner = RDSScanner(region=region, profile=profile)
                results = scanner.scan_databases()
                all_results.extend(results)
            except Exception as e:
                print(f"Error scanning profile '{profile}' in region '{region}': {e}")
                continue
    
    if all_results:
        export_to_csv(all_results, args.output)
        export_to_json(all_results, args.json_output)
        print_summary(all_results)
        
        # Send Slack notification if webhook provided
        if args.slack_webhook:
            try:
                from slack_notifier import SlackNotifier
                print(f"\n{'='*80}")
                print("Sending Slack notification...")
                print(f"{'='*80}")
                
                notifier = SlackNotifier(args.slack_webhook)
                notifier.send_scan_results(all_results, args.s3_url)
            except ImportError:
                print("Warning: slack_notifier module not found. Install requests: pip install requests")
            except Exception as e:
                print(f"Error sending Slack notification: {e}")
    else:
        print("No databases found or error occurred during scanning")


if __name__ == '__main__':
    main()
