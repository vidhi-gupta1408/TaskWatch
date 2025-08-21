import os
import csv
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import pytz
from celery import Task
from app import celery, db
from app.models.db_models import StoreStatus, BusinessHours, Timezone, Report
from app.utils.time_helpers import convert_utc_to_local, get_business_hours_for_day

class CallbackTask(Task):
    """Custom task class to ensure Flask app context"""
    def __call__(self, *args, **kwargs):
        from app import create_app
        app = create_app()
        with app.app_context():
            return self.run(*args, **kwargs)

@celery.task(base=CallbackTask, bind=True)
def generate_report_task(self, report_id: str):
    """
    Background task to generate store uptime/downtime report.
    """
    try:
        logging.info(f"Starting report generation for ID: {report_id}")
        
        # Update report status
        report = Report.query.filter_by(report_id=report_id).first()
        if not report:
            raise Exception(f"Report {report_id} not found")
        
        # Get current timestamp from data
        current_time = get_current_timestamp()
        logging.info(f"Using current timestamp: {current_time}")
        
        # Generate report data
        report_data = generate_store_metrics(current_time)
        
        # Save to CSV file
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        csv_path = os.path.join(reports_dir, f'report_{report_id}.csv')
        save_report_to_csv(report_data, csv_path)
        
        # Update report in database
        report.status = 'Complete'
        report.report_path = csv_path
        db.session.commit()
        
        logging.info(f"Report generation completed for ID: {report_id}")
        return f"Report generated successfully at {csv_path}"
        
    except Exception as e:
        logging.error(f"Error generating report {report_id}: {e}")
        
        # Update report status to failed
        try:
            report = Report.query.filter_by(report_id=report_id).first()
            if report:
                report.status = 'Failed'
                db.session.commit()
        except Exception as db_error:
            logging.error(f"Failed to update report status: {db_error}")
        
        raise e

def generate_report_sync(report_id: str) -> str:
    """
    Synchronous report generation for when Redis/Celery is unavailable.
    """
    try:
        logging.info(f"Starting synchronous report generation for ID: {report_id}")
        
        # Update report status
        report = Report.query.filter_by(report_id=report_id).first()
        if not report:
            raise Exception(f"Report {report_id} not found")
        
        # Get current timestamp from data
        current_time = get_current_timestamp()
        logging.info(f"Using current timestamp: {current_time}")
        
        # Generate report data
        report_data = generate_store_metrics(current_time)
        
        # Save to CSV file
        reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        csv_path = os.path.join(reports_dir, f'report_{report_id}.csv')
        save_report_to_csv(report_data, csv_path)
        
        # Update report in database
        report.status = 'Complete'
        report.report_path = csv_path
        db.session.commit()
        
        logging.info(f"Synchronous report generation completed for ID: {report_id}")
        return csv_path
        
    except Exception as e:
        logging.error(f"Error in synchronous report generation {report_id}: {e}")
        
        # Update report status to failed
        try:
            report = Report.query.filter_by(report_id=report_id).first()
            if report:
                report.status = 'Failed'
                db.session.commit()
        except Exception as db_error:
            logging.error(f"Failed to update report status: {db_error}")
        
        raise e

def get_current_timestamp() -> datetime:
    """
    Get the current timestamp as the maximum timestamp from store_status data.
    """
    max_timestamp = db.session.query(
        db.func.max(StoreStatus.timestamp_utc)
    ).scalar()
    
    if not max_timestamp:
        # Fallback to current time if no data exists
        return datetime.utcnow()
    
    return max_timestamp

def generate_store_metrics(current_time: datetime) -> List[Dict]:
    """
    Generate uptime/downtime metrics for all stores.
    """
    # Get all unique store IDs
    store_ids = db.session.query(StoreStatus.store_id).distinct().all()
    store_ids = [sid[0] for sid in store_ids]
    
    logging.info(f"Processing {len(store_ids)} stores")
    
    report_data = []
    
    for store_id in store_ids:
        try:
            metrics = calculate_store_metrics(store_id, current_time)
            report_data.append(metrics)
            
            if len(report_data) % 100 == 0:
                logging.info(f"Processed {len(report_data)} stores")
                
        except Exception as e:
            logging.error(f"Error processing store {store_id}: {e}")
            # Add default metrics for failed stores
            report_data.append({
                'store_id': store_id,
                'uptime_last_hour': 0,
                'uptime_last_day': 0,
                'uptime_last_week': 0,
                'downtime_last_hour': 0,
                'downtime_last_day': 0,
                'downtime_last_week': 0
            })
    
    return report_data

def calculate_store_metrics(store_id: int, current_time: datetime) -> Dict:
    """
    Calculate uptime/downtime metrics for a specific store.
    """
    # Get store timezone
    timezone_str = get_store_timezone(store_id)
    local_tz = pytz.timezone(timezone_str)
    
    # Define time periods
    hour_ago = current_time - timedelta(hours=1)
    day_ago = current_time - timedelta(days=1)
    week_ago = current_time - timedelta(weeks=1)
    
    # Get status observations for the week
    status_observations = db.session.query(StoreStatus).filter(
        StoreStatus.store_id == store_id,
        StoreStatus.timestamp_utc >= week_ago,
        StoreStatus.timestamp_utc <= current_time
    ).order_by(StoreStatus.timestamp_utc).all()
    
    # Calculate metrics for each period
    uptime_last_hour, downtime_last_hour = calculate_period_metrics(
        store_id, status_observations, hour_ago, current_time, local_tz, 'minutes'
    )
    
    uptime_last_day, downtime_last_day = calculate_period_metrics(
        store_id, status_observations, day_ago, current_time, local_tz, 'hours'
    )
    
    uptime_last_week, downtime_last_week = calculate_period_metrics(
        store_id, status_observations, week_ago, current_time, local_tz, 'hours'
    )
    
    return {
        'store_id': store_id,
        'uptime_last_hour': round(uptime_last_hour, 2),
        'uptime_last_day': round(uptime_last_day, 2),
        'uptime_last_week': round(uptime_last_week, 2),
        'downtime_last_hour': round(downtime_last_hour, 2),
        'downtime_last_day': round(downtime_last_day, 2),
        'downtime_last_week': round(downtime_last_week, 2)
    }

def calculate_period_metrics(
    store_id: int, 
    observations: List[StoreStatus], 
    start_time: datetime, 
    end_time: datetime,
    local_tz: Any,
    unit: str
) -> Tuple[float, float]:
    """
    Calculate uptime and downtime for a specific period.
    """
    total_uptime = 0.0
    total_downtime = 0.0
    
    # Filter observations within the period
    period_observations = [
        obs for obs in observations 
        if start_time <= obs.timestamp_utc <= end_time
    ]
    
    # If no observations, assume store was closed
    if not period_observations:
        return 0.0, 0.0
    
    # Get business hours for the period
    business_intervals = get_business_intervals(store_id, start_time, end_time, local_tz)
    
    # Calculate uptime/downtime for each business interval
    for interval_start, interval_end in business_intervals:
        # Convert to UTC for comparison
        interval_start_utc = interval_start.astimezone(pytz.UTC).replace(tzinfo=None)
        interval_end_utc = interval_end.astimezone(pytz.UTC).replace(tzinfo=None)
        
        # Get observations within this business interval
        interval_obs = [
            obs for obs in period_observations
            if interval_start_utc <= obs.timestamp_utc <= interval_end_utc
        ]
        
        # Calculate uptime/downtime using interpolation
        uptime, downtime = interpolate_status_in_interval(
            interval_obs, interval_start_utc, interval_end_utc
        )
        
        total_uptime += uptime
        total_downtime += downtime
    
    # Convert to requested units
    if unit == 'minutes':
        total_uptime = total_uptime / 60.0
        total_downtime = total_downtime / 60.0
    elif unit == 'hours':
        total_uptime = total_uptime / 3600.0
        total_downtime = total_downtime / 3600.0
    
    return total_uptime, total_downtime

def interpolate_status_in_interval(
    observations: List[StoreStatus], 
    start_time: datetime, 
    end_time: datetime
) -> Tuple[float, float]:
    """
    Interpolate status within a business interval using the specified logic.
    """
    if not observations:
        return 0.0, 0.0
    
    total_seconds = (end_time - start_time).total_seconds()
    uptime_seconds = 0.0
    
    # Sort observations by timestamp
    observations.sort(key=lambda x: x.timestamp_utc)
    
    # Handle period before first observation
    first_obs = observations[0]
    if start_time < first_obs.timestamp_utc:
        period_seconds = (first_obs.timestamp_utc - start_time).total_seconds()
        if first_obs.status == 'active':
            uptime_seconds += period_seconds
    
    # Handle periods between observations
    for i in range(len(observations) - 1):
        current_obs = observations[i]
        next_obs = observations[i + 1]
        
        period_seconds = (next_obs.timestamp_utc - current_obs.timestamp_utc).total_seconds()
        if current_obs.status == 'active':
            uptime_seconds += period_seconds
    
    # Handle period after last observation
    last_obs = observations[-1]
    if end_time > last_obs.timestamp_utc:
        period_seconds = (end_time - last_obs.timestamp_utc).total_seconds()
        if last_obs.status == 'active':
            uptime_seconds += period_seconds
    
    downtime_seconds = total_seconds - uptime_seconds
    
    return uptime_seconds, downtime_seconds

def get_business_intervals(
    store_id: int, 
    start_time: datetime, 
    end_time: datetime,
    local_tz: Any
) -> List[Tuple[datetime, datetime]]:
    """
    Get all business hour intervals for a store within the given time period.
    """
    intervals = []
    
    # Get business hours for the store
    business_hours = db.session.query(BusinessHours).filter(
        BusinessHours.store_id == store_id
    ).all()
    
    # If no business hours defined, assume 24/7 operation
    if not business_hours:
        intervals.append((
            start_time.replace(tzinfo=pytz.UTC).astimezone(local_tz),
            end_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
        ))
        return intervals
    
    # Convert times to local timezone
    start_local = start_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    end_local = end_time.replace(tzinfo=pytz.UTC).astimezone(local_tz)
    
    # Iterate through each day in the period
    current_day = start_local.date()
    end_day = end_local.date()
    
    while current_day <= end_day:
        day_of_week = current_day.weekday()  # 0=Monday, 6=Sunday
        
        # Get business hours for this day
        day_hours = [bh for bh in business_hours if bh.dayOfWeek == day_of_week]
        
        for hours in day_hours:
            # Create datetime objects for business hours
            business_start = local_tz.localize(
                datetime.combine(current_day, hours.start_time_local)
            )
            business_end = local_tz.localize(
                datetime.combine(current_day, hours.end_time_local)
            )
            
            # Handle overnight business hours
            if hours.end_time_local < hours.start_time_local:
                business_end += timedelta(days=1)
            
            # Clip to the requested period
            interval_start = max(business_start, start_local)
            interval_end = min(business_end, end_local)
            
            if interval_start < interval_end:
                intervals.append((interval_start, interval_end))
        
        current_day += timedelta(days=1)
    
    return intervals

def get_store_timezone(store_id: int) -> str:
    """
    Get timezone for a store, defaulting to America/Chicago if not found.
    """
    timezone_record = db.session.query(Timezone).filter(
        Timezone.store_id == store_id
    ).first()
    
    if timezone_record:
        return timezone_record.timezone_str
    else:
        return 'America/Chicago'

def save_report_to_csv(report_data: List[Dict], csv_path: str):
    """
    Save report data to CSV file with the required schema.
    """
    fieldnames = [
        'store_id',
        'uptime_last_hour',
        'uptime_last_day', 
        'uptime_last_week',
        'downtime_last_hour',
        'downtime_last_day',
        'downtime_last_week'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in report_data:
            writer.writerow(row)
    
    logging.info(f"Report saved to {csv_path} with {len(report_data)} stores")
