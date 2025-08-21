import os
import csv
import logging
from datetime import datetime, time
from typing import Optional
import pandas as pd
from app import db
from app.models.db_models import StoreStatus, BusinessHours, Timezone

def load_data():
    """
    Load data from CSV files into the database.
    This operation is idempotent - it can be run multiple times safely.
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
    
    # Load each CSV file
    load_store_status(os.path.join(data_dir, 'store_status.csv'))
    load_business_hours(os.path.join(data_dir, 'menu_hours.csv'))
    load_timezones(os.path.join(data_dir, 'timezone.csv'))

def load_store_status(csv_path: str):
    """
    Load store status data from CSV.
    """
    if not os.path.exists(csv_path):
        logging.warning(f"Store status CSV not found at {csv_path}")
        return
    
    logging.info(f"Loading store status data from {csv_path}")
    
    # Clear existing data
    db.session.query(StoreStatus).delete()
    
    try:
        df = pd.read_csv(csv_path)
        
        records_added = 0
        for _, row in df.iterrows():
            try:
                # Parse timestamp
                timestamp_str = str(row['timestamp_utc'])
                # Handle different timestamp formats
                timestamp_utc = parse_timestamp(timestamp_str)
                
                status_record = StoreStatus(
                    store_id=str(row['store_id']),
                    timestamp_utc=timestamp_utc,
                    status=str(row['status'])
                )
                
                db.session.add(status_record)
                records_added += 1
                
                # Commit in batches for better performance
                if records_added % 1000 == 0:
                    db.session.commit()
                    logging.info(f"Loaded {records_added} store status records")
                    
            except Exception as e:
                logging.error(f"Error processing store status row: {row}, error: {e}")
                continue
        
        db.session.commit()
        logging.info(f"Successfully loaded {records_added} store status records")
        
    except Exception as e:
        logging.error(f"Error loading store status data: {e}")
        db.session.rollback()
        raise

def load_business_hours(csv_path: str):
    """
    Load business hours data from CSV.
    """
    if not os.path.exists(csv_path):
        logging.warning(f"Business hours CSV not found at {csv_path}")
        return
    
    logging.info(f"Loading business hours data from {csv_path}")
    
    # Clear existing data
    db.session.query(BusinessHours).delete()
    
    try:
        df = pd.read_csv(csv_path)
        
        records_added = 0
        for _, row in df.iterrows():
            try:
                # Parse times
                start_time = parse_time(str(row['start_time_local']))
                end_time = parse_time(str(row['end_time_local']))
                
                business_hours = BusinessHours(
                    store_id=str(row['store_id']),
                    dayOfWeek=int(row['dayOfWeek']),
                    start_time_local=start_time,
                    end_time_local=end_time
                )
                
                db.session.add(business_hours)
                records_added += 1
                
            except Exception as e:
                logging.error(f"Error processing business hours row: {row}, error: {e}")
                continue
        
        db.session.commit()
        logging.info(f"Successfully loaded {records_added} business hours records")
        
    except Exception as e:
        logging.error(f"Error loading business hours data: {e}")
        db.session.rollback()
        raise

def load_timezones(csv_path: str):
    """
    Load timezone data from CSV.
    """
    if not os.path.exists(csv_path):
        logging.warning(f"Timezone CSV not found at {csv_path}")
        return
    
    logging.info(f"Loading timezone data from {csv_path}")
    
    # Clear existing data
    db.session.query(Timezone).delete()
    
    try:
        df = pd.read_csv(csv_path)
        
        records_added = 0
        for _, row in df.iterrows():
            try:
                timezone_record = Timezone(
                    store_id=str(row['store_id']),
                    timezone_str=str(row['timezone_str'])
                )
                
                db.session.add(timezone_record)
                records_added += 1
                
            except Exception as e:
                logging.error(f"Error processing timezone row: {row}, error: {e}")
                continue
        
        db.session.commit()
        logging.info(f"Successfully loaded {records_added} timezone records")
        
    except Exception as e:
        logging.error(f"Error loading timezone data: {e}")
        db.session.rollback()
        raise

def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp string into datetime object.
    Handles multiple common formats.
    """
    # Common timestamp formats
    formats = [
        '%Y-%m-%d %H:%M:%S.%f %Z',  # 2023-01-25 12:05:19.846849 UTC
        '%Y-%m-%d %H:%M:%S %Z',     # 2023-01-25 12:05:19 UTC
        '%Y-%m-%d %H:%M:%S.%f',     # 2023-01-25 12:05:19.846849
        '%Y-%m-%d %H:%M:%S',        # 2023-01-25 12:05:19
        '%Y-%m-%dT%H:%M:%S.%fZ',    # 2023-01-25T12:05:19.846849Z
        '%Y-%m-%dT%H:%M:%SZ',       # 2023-01-25T12:05:19Z
        '%Y-%m-%dT%H:%M:%S.%f',     # 2023-01-25T12:05:19.846849
        '%Y-%m-%dT%H:%M:%S',        # 2023-01-25T12:05:19
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(timestamp_str, fmt)
        except ValueError:
            continue
    
    # If none of the formats work, try pandas parsing
    try:
        return pd.to_datetime(timestamp_str).to_pydatetime()
    except Exception:
        raise ValueError(f"Unable to parse timestamp: {timestamp_str}")

def parse_time(time_str: str) -> time:
    """
    Parse time string into time object.
    """
    # Common time formats
    formats = [
        '%H:%M:%S',  # 09:00:00
        '%H:%M',     # 09:00
        '%I:%M:%S %p',  # 09:00:00 AM
        '%I:%M %p',     # 09:00 AM
    ]
    
    for fmt in formats:
        try:
            time_obj = datetime.strptime(time_str, fmt).time()
            return time_obj
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse time: {time_str}")
