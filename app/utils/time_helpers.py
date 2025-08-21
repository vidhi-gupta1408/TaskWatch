import pytz
from datetime import datetime, time
from typing import Optional, Tuple

def convert_utc_to_local(utc_dt: datetime, timezone_str: str) -> datetime:
    """
    Convert UTC datetime to local timezone.
    
    Args:
        utc_dt: UTC datetime object (timezone naive)
        timezone_str: Target timezone string (e.g., 'America/Chicago')
    
    Returns:
        Local datetime object with timezone info
    """
    utc_tz = pytz.UTC
    local_tz = pytz.timezone(timezone_str)
    
    # Ensure UTC datetime has timezone info
    if utc_dt.tzinfo is None:
        utc_dt = utc_tz.localize(utc_dt)
    
    # Convert to local timezone
    local_dt = utc_dt.astimezone(local_tz)
    
    return local_dt

def convert_local_to_utc(local_dt: datetime, timezone_str: str) -> datetime:
    """
    Convert local datetime to UTC.
    
    Args:
        local_dt: Local datetime object (timezone naive)
        timezone_str: Source timezone string (e.g., 'America/Chicago')
    
    Returns:
        UTC datetime object (timezone naive)
    """
    local_tz = pytz.timezone(timezone_str)
    
    # Localize the datetime if it's naive
    if local_dt.tzinfo is None:
        local_dt = local_tz.localize(local_dt)
    
    # Convert to UTC and remove timezone info
    utc_dt = local_dt.astimezone(pytz.UTC)
    return utc_dt.replace(tzinfo=None)

def get_business_hours_for_day(day_of_week: int, business_hours: list) -> list:
    """
    Get business hours for a specific day of the week.
    
    Args:
        day_of_week: Day of week (0=Monday, 6=Sunday)
        business_hours: List of BusinessHours objects
    
    Returns:
        List of (start_time, end_time) tuples for the day
    """
    day_hours = []
    
    for bh in business_hours:
        if bh.dayOfWeek == day_of_week:
            day_hours.append((bh.start_time_local, bh.end_time_local))
    
    return day_hours

def is_within_business_hours(
    local_dt: datetime, 
    start_time: time, 
    end_time: time
) -> bool:
    """
    Check if a local datetime falls within business hours.
    
    Args:
        local_dt: Local datetime to check
        start_time: Business start time
        end_time: Business end time
    
    Returns:
        True if within business hours, False otherwise
    """
    current_time = local_dt.time()
    
    # Handle overnight business hours (e.g., 22:00 to 06:00)
    if end_time < start_time:
        # Business hours cross midnight
        return current_time >= start_time or current_time <= end_time
    else:
        # Normal business hours within same day
        return start_time <= current_time <= end_time

def get_timezone_offset_hours(timezone_str: str, dt: datetime) -> float:
    """
    Get timezone offset in hours for a given datetime.
    
    Args:
        timezone_str: Timezone string (e.g., 'America/Chicago')
        dt: Datetime object
    
    Returns:
        Offset in hours (can be negative)
    """
    tz = pytz.timezone(timezone_str)
    
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = pytz.UTC.localize(dt)
    
    local_dt = dt.astimezone(tz)
    offset = local_dt.utcoffset()
    if offset is None:
        return 0.0
    offset_seconds = offset.total_seconds()
    
    return offset_seconds / 3600.0

def datetime_range(start: datetime, end: datetime, step_hours: int = 1):
    """
    Generate datetime range with specified step.
    
    Args:
        start: Start datetime
        end: End datetime  
        step_hours: Step size in hours
    
    Yields:
        Datetime objects in the range
    """
    from datetime import timedelta
    
    current = start
    step = timedelta(hours=step_hours)
    
    while current <= end:
        yield current
        current += step

def validate_timezone(timezone_str: str) -> bool:
    """
    Validate if a timezone string is valid.
    
    Args:
        timezone_str: Timezone string to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        pytz.timezone(timezone_str)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False

def get_day_boundaries_local(dt: datetime, timezone_str: str) -> Tuple[datetime, datetime]:
    """
    Get start and end of day boundaries in local timezone.
    
    Args:
        dt: Reference datetime
        timezone_str: Timezone string
    
    Returns:
        Tuple of (day_start, day_end) in local timezone
    """
    local_tz = pytz.timezone(timezone_str)
    
    # Convert to local timezone
    if dt.tzinfo is None:
        dt = pytz.UTC.localize(dt)
    
    local_dt = dt.astimezone(local_tz)
    
    # Get start of day (midnight)
    day_start = local_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get end of day (23:59:59.999999)
    day_end = local_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    return day_start, day_end
