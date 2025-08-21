#!/usr/bin/env python3
"""
Generate store status data for the new UUID-based store system
"""

import csv
import random
from datetime import datetime, timedelta
import pandas as pd

def generate_store_status_data():
    """Generate realistic store status data for UUID stores"""
    
    # Get store IDs from both files to ensure consistency
    print("Reading store IDs from menu_hours.csv...")
    menu_df = pd.read_csv('data/menu_hours.csv')
    store_ids = menu_df['store_id'].unique().tolist()
    
    print(f"Found {len(store_ids)} unique stores")
    
    # Generate timestamps for the last 7 days
    end_time = datetime(2023, 1, 26, 17, 0, 0)  # Match the original timestamp
    start_time = end_time - timedelta(days=7)
    
    status_records = []
    
    print("Generating store status data...")
    
    for store_id in store_ids:
        # Generate random status changes for each store
        current_time = start_time
        current_status = random.choice(['active', 'inactive'])
        
        # Generate 20-50 status changes per store over the week
        num_changes = random.randint(20, 50)
        
        for i in range(num_changes):
            # Add timestamp
            status_records.append({
                'store_id': store_id,
                'status': current_status,
                'timestamp_utc': current_time.strftime('%Y-%m-%d %H:%M:%S.%f UTC')
            })
            
            # Move to next timestamp (random interval between 1-8 hours)
            hours_forward = random.uniform(1, 8)
            current_time += timedelta(hours=hours_forward)
            
            # Stop if we exceed end time
            if current_time > end_time:
                break
            
            # Randomly flip status (80% chance to stay same, 20% chance to flip)
            if random.random() < 0.2:
                current_status = 'inactive' if current_status == 'active' else 'active'
    
    # Sort by timestamp
    status_records.sort(key=lambda x: x['timestamp_utc'])
    
    print(f"Generated {len(status_records)} status records")
    
    # Write to CSV
    with open('data/store_status.csv', 'w', newline='') as csvfile:
        fieldnames = ['store_id', 'status', 'timestamp_utc']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for record in status_records:
            writer.writerow(record)
    
    print("Store status data written to data/store_status.csv")
    
    # Show sample data
    print("\nSample records:")
    for i, record in enumerate(status_records[:10]):
        print(f"  {record['store_id'][:8]}... | {record['status']} | {record['timestamp_utc']}")
    
    return len(status_records), len(store_ids)

if __name__ == "__main__":
    num_records, num_stores = generate_store_status_data()
    print(f"\n✅ Successfully generated {num_records} status records for {num_stores} stores")