#!/usr/bin/env python3
"""
Lambda Storage Scanner
Identifies Lambda functions consuming excessive storage and unused functions.
Helps address Lambda 300GB storage limit issues.
"""

import boto3
import csv
import json
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import argparse


class LambdaStorageScanner:
    def __init__(self, region='us-west-2', profile=None):
        """Initialize Lambda Storage Scanner."""
        session = boto3.Session(profile_name=profile, region_name=region) if profile else boto3.Session(region_name=region)
        self.lambda_client = session.client('lambda', region_name=region)
        self.cloudwatch = session.client('cloudwatch', region_name=region)
        self.region = region

    def get_all_functions(self):
        """Get all Lambda functions in the account."""
        functions = []
        paginator = self.lambda_client.get_paginator('list_functions')

        for page in paginator.paginate():
            functions.extend(page['Functions'])

        print(f"Found {len(functions)} Lambda functions in {self.region}")
        return functions

    def get_function_versions(self, function_name):
        """Get all versions for a Lambda function."""
        versions = []
        paginator = self.lambda_client.get_paginator('list_versions_by_function')

        try:
            for page in paginator.paginate(FunctionName=function_name):
                versions.extend(page['Versions'])
        except Exception as e:
            print(f"Error getting versions for {function_name}: {e}")

        return versions

    def get_function_tags(self, function_arn):
        """Get tags for a Lambda function."""
        try:
            response = self.lambda_client.list_tags(Resource=function_arn)
            tags = response.get('Tags', {})
            return {
                'owner': tags.get('Owner', tags.get('owner', 'N/A')),
                'contact': tags.get('Contact', tags.get('contact', 'N/A')),
                'repo': tags.get('Repo', tags.get('repo', tags.get('Repository', 'N/A'))),
                'environment': tags.get('Environment', tags.get('environment', 'N/A')),
                'team': tags.get('Team', tags.get('team', 'N/A'))
            }
        except Exception as e:
            print(f"Error getting tags for {function_arn}: {e}")
            return {
                'owner': 'N/A',
                'contact': 'N/A',
                'repo': 'N/A',
                'environment': 'N/A',
                'team': 'N/A'
            }

    def get_invocation_count(self, function_name, days=30):
        """Get invocation count for last N days."""
        try:
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=days)

            response = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/Lambda',
                MetricName='Invocations',
                Dimensions=[{'Name': 'FunctionName', 'Value': function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400 * days,  # Total for the period
                Statistics=['Sum']
            )

            if response['Datapoints']:
                return int(response['Datapoints'][0]['Sum'])
            return 0
        except Exception as e:
            print(f"Error getting invocations for {function_name}: {e}")
            return 0

    def calculate_storage_usage(self, function_name, versions):
        """Calculate total storage usage for a function and all its versions."""
        total_storage = 0

        for version in versions:
            code_size = version.get('CodeSize', 0)
            total_storage += code_size

        return total_storage

    def analyze_function(self, function):
        """Analyze a single Lambda function."""
        function_name = function['FunctionName']
        function_arn = function['FunctionArn']

        print(f"Analyzing: {function_name}...")

        # Get versions
        versions = self.get_function_versions(function_name)
        version_count = len(versions)

        # Calculate storage
        total_storage_bytes = self.calculate_storage_usage(function_name, versions)
        total_storage_mb = total_storage_bytes / (1024 * 1024)

        # Get invocation count
        invocations_30d = self.get_invocation_count(function_name, days=30)
        invocations_7d = self.get_invocation_count(function_name, days=7)

        # Get tags
        tags = self.get_function_tags(function_arn)

        # Categorize function
        category = self.categorize_function(version_count, total_storage_mb, invocations_30d)

        # Get latest version info
        latest_version = function
        runtime = latest_version.get('Runtime', 'N/A')
        last_modified = latest_version.get('LastModified', 'N/A')
        code_size_mb = latest_version.get('CodeSize', 0) / (1024 * 1024)

        return {
            'function_name': function_name,
            'runtime': runtime,
            'version_count': version_count,
            'latest_version_size_mb': round(code_size_mb, 2),
            'total_storage_mb': round(total_storage_mb, 2),
            'invocations_30d': invocations_30d,
            'invocations_7d': invocations_7d,
            'last_modified': last_modified,
            'category': category,
            'recommendation': self.get_recommendation(category, version_count, invocations_30d),
            'owner': tags['owner'],
            'contact': tags['contact'],
            'repo': tags['repo'],
            'environment': tags['environment'],
            'team': tags['team'],
            'region': self.region
        }

    def categorize_function(self, version_count, storage_mb, invocations):
        """Categorize function based on usage and storage."""
        if invocations == 0:
            return "UNUSED"
        elif version_count > 10:
            return "VERSION_BLOAT"
        elif storage_mb > 100:
            return "LARGE_STORAGE"
        elif invocations < 10:
            return "LOW_USAGE"
        else:
            return "ACTIVE"

    def get_recommendation(self, category, version_count, invocations):
        """Get recommendation based on category."""
        recommendations = {
            "UNUSED": f"DELETE - No invocations in 30 days. Has {version_count} versions consuming storage.",
            "VERSION_BLOAT": f"CLEANUP_VERSIONS - Has {version_count} versions. Keep only recent versions.",
            "LARGE_STORAGE": f"OPTIMIZE - Large deployment package. Consider optimization or S3 layers.",
            "LOW_USAGE": f"REVIEW - Only {invocations} invocations in 30 days. Consider deletion.",
            "ACTIVE": "OK - Actively used with reasonable storage."
        }
        return recommendations.get(category, "REVIEW")

    def scan_all_functions(self):
        """Scan all Lambda functions and return analysis."""
        functions = self.get_all_functions()
        results = []

        total_storage = 0

        for function in functions:
            result = self.analyze_function(function)
            results.append(result)
            total_storage += result['total_storage_mb']

        # Sort by total storage (highest first)
        results.sort(key=lambda x: x['total_storage_mb'], reverse=True)

        print(f"\n{'='*80}")
        print(f"SCAN COMPLETE")
        print(f"{'='*80}")
        print(f"Total Functions: {len(results)}")
        print(f"Total Storage: {total_storage:,.2f} MB ({total_storage/1024:.2f} GB)")
        print(f"Storage Limit: 300 GB")
        print(f"Storage Used: {(total_storage/1024/300)*100:.1f}%")

        # Category breakdown
        categories = defaultdict(int)
        for result in results:
            categories[result['category']] += 1

        print(f"\nCategory Breakdown:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")

        return results, total_storage

    def export_to_csv(self, results, filename=None):
        """Export results to CSV file."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'lambda_storage_scan_{timestamp}.csv'

        fieldnames = [
            'function_name',
            'category',
            'recommendation',
            'total_storage_mb',
            'version_count',
            'latest_version_size_mb',
            'invocations_30d',
            'invocations_7d',
            'runtime',
            'last_modified',
            'owner',
            'contact',
            'repo',
            'team',
            'environment',
            'region'
        ]

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✓ Results exported to: {filename}")
        return filename

    def print_summary(self, results, total_storage):
        """Print summary of top storage consumers."""
        print(f"\n{'='*80}")
        print(f"TOP 10 STORAGE CONSUMERS")
        print(f"{'='*80}")
        print(f"{'Function Name':<50} {'Storage (MB)':<15} {'Versions':<10} {'Category'}")
        print(f"{'-'*50} {'-'*15} {'-'*10} {'-'*20}")

        for result in results[:10]:
            print(f"{result['function_name']:<50} {result['total_storage_mb']:<15.2f} {result['version_count']:<10} {result['category']}")

        print(f"\n{'='*80}")
        print(f"FUNCTIONS TO DELETE (UNUSED)")
        print(f"{'='*80}")

        unused = [r for r in results if r['category'] == 'UNUSED']
        if unused:
            print(f"Found {len(unused)} unused functions")
            print(f"{'Function Name':<50} {'Storage (MB)':<15} {'Owner'}")
            print(f"{'-'*50} {'-'*15} {'-'*30}")

            for result in unused[:20]:
                print(f"{result['function_name']:<50} {result['total_storage_mb']:<15.2f} {result['owner']}")

            unused_storage = sum(r['total_storage_mb'] for r in unused)
            print(f"\nPotential storage savings from deleting unused: {unused_storage:.2f} MB ({unused_storage/1024:.2f} GB)")
        else:
            print("No unused functions found.")


def main():
    parser = argparse.ArgumentParser(description='Scan Lambda functions for storage issues')
    parser.add_argument('--region', default='us-west-2', help='AWS region (default: us-west-2)')
    parser.add_argument('--profile', help='AWS profile to use')
    parser.add_argument('--output', help='Output CSV filename')

    args = parser.parse_args()

    print(f"{'='*80}")
    print(f"Lambda Storage Scanner")
    print(f"{'='*80}")
    print(f"Region: {args.region}")
    if args.profile:
        print(f"Profile: {args.profile}")
    print(f"{'='*80}\n")

    scanner = LambdaStorageScanner(region=args.region, profile=args.profile)

    # Scan all functions
    results, total_storage = scanner.scan_all_functions()

    # Export to CSV
    csv_file = scanner.export_to_csv(results, args.output)

    # Print summary
    scanner.print_summary(results, total_storage)

    print(f"\n{'='*80}")
    print(f"NEXT STEPS:")
    print(f"{'='*80}")
    print(f"1. Review CSV file: {csv_file}")
    print(f"2. Contact function owners to delete UNUSED functions")
    print(f"3. Clean up old versions for VERSION_BLOAT functions")
    print(f"4. Optimize LARGE_STORAGE functions")
    print(f"\nTo delete old versions of a function:")
    print(f"  aws lambda delete-function --function-name FUNCTION_NAME --qualifier VERSION_NUMBER")
    print(f"\nTo delete an entire function:")
    print(f"  aws lambda delete-function --function-name FUNCTION_NAME")


if __name__ == "__main__":
    main()
