from app import db
from datetime import datetime
from typing import Optional

class StoreStatus(db.Model):
    """
    Store status observations from CSV data.
    """
    __tablename__ = 'store_status'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False, index=True)  # Changed to String for UUID
    timestamp_utc = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False)  # 'active' or 'inactive'
    
    def __init__(self, store_id, timestamp_utc, status):
        self.store_id = store_id
        self.timestamp_utc = timestamp_utc
        self.status = status
    
    def __repr__(self):
        return f'<StoreStatus {self.store_id}: {self.status} at {self.timestamp_utc}>'

class BusinessHours(db.Model):
    """
    Business hours for each store by day of week.
    """
    __tablename__ = 'business_hours'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False, index=True)  # Changed to String for UUID
    dayOfWeek = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time_local = db.Column(db.Time, nullable=False)
    end_time_local = db.Column(db.Time, nullable=False)
    
    def __init__(self, store_id, dayOfWeek, start_time_local, end_time_local):
        self.store_id = store_id
        self.dayOfWeek = dayOfWeek
        self.start_time_local = start_time_local
        self.end_time_local = end_time_local
    
    def __repr__(self):
        return f'<BusinessHours {self.store_id}: Day {self.dayOfWeek} {self.start_time_local}-{self.end_time_local}>'

class Timezone(db.Model):
    """
    Timezone information for each store.
    """
    __tablename__ = 'timezone'
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False, unique=True, index=True)  # Changed to String for UUID
    timezone_str = db.Column(db.String(50), nullable=False)
    
    def __init__(self, store_id, timezone_str):
        self.store_id = store_id
        self.timezone_str = timezone_str
    
    def __repr__(self):
        return f'<Timezone {self.store_id}: {self.timezone_str}>'

class Report(db.Model):
    """
    Generated reports and their status.
    """
    __tablename__ = 'report'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.String(36), nullable=False, unique=True, index=True)
    status = db.Column(db.String(20), nullable=False)  # 'Running', 'Complete', 'Failed'
    report_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, report_id, status, report_path=None):
        self.report_id = report_id
        self.status = status
        self.report_path = report_path
    
    def __repr__(self):
        return f'<Report {self.report_id}: {self.status}>'
