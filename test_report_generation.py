#!/usr/bin/env python3
"""
Test script to demonstrate report generation functionality
without Celery/Redis dependencies.
"""

import os
import sys
import logging
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, '.')

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_report_generation():
    """Test the report generation functionality directly."""
    try:
        from app import create_app
        from app.core.reporter import (
            get_current_timestamp, 
            generate_store_metrics, 
            save_report_to_csv
        )
        
        # Create app context
        app = create_app()
        
        with app.app_context():
            print("=" * 60)
            print("STORE MONITORING SYSTEM - REPORT GENERATION TEST")
            print("=" * 60)
            
            # Get current timestamp
            current_time = get_current_timestamp()
            print(f"Current timestamp from data: {current_time}")
            
            # Generate report data
            print("\nGenerating store metrics...")
            report_data = generate_store_metrics(current_time)
            
            print(f"Generated metrics for {len(report_data)} stores")
            
            # Display sample results
            print("\nSample Store Metrics:")
            print("-" * 60)
            for i, store_data in enumerate(report_data[:3]):  # Show first 3 stores
                print(f"Store {store_data['store_id']}:")
                print(f"  Last Hour:  {store_data['uptime_last_hour']:.1f}min up, {store_data['downtime_last_hour']:.1f}min down")
                print(f"  Last Day:   {store_data['uptime_last_day']:.1f}hr up, {store_data['downtime_last_day']:.1f}hr down") 
                print(f"  Last Week:  {store_data['uptime_last_week']:.1f}hr up, {store_data['downtime_last_week']:.1f}hr down")
                print()
            
            # Save to CSV
            csv_path = "sample_report.csv"
            save_report_to_csv(report_data, csv_path)
            print(f"Report saved to: {csv_path}")
            
            # Show CSV content
            print(f"\nFirst 5 lines of generated CSV:")
            print("-" * 60)
            with open(csv_path, 'r') as f:
                for i, line in enumerate(f):
                    if i < 5:
                        print(line.strip())
            
            print("\n" + "=" * 60)
            print("REPORT GENERATION TEST COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            
    except Exception as e:
        print(f"Error in report generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_report_generation()