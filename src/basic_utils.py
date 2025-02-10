
import os
from datetime import datetime

def get_date(format='date'):
    current_time = datetime.now()

    if format == 'date':
        return current_time.strftime("%Y%m%d")
    elif format == 'date-':
        return current_time.strftime("%Y-%m-%d")
    elif format == 'datetime':
        return current_time.strftime("%Y%m%d_%H_%M")
def convert_timestamps(timestamp):
    # from 1729591222585
    # Convert the timestamp to YYYY-MM-DD format
    timestamp = timestamp / 1000  # Convert from milliseconds to seconds
    yyyymmdd = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    return yyyymmdd


def convert_ms_to_iso8601(timestamp_ms):
    # Convert milliseconds to seconds for Python's datetime
    timestamp_sec = timestamp_ms / 1000
    # Convert to datetime object
    dt = datetime.utcfromtimestamp(timestamp_sec)
    # Format to ISO 8601
    return dt.isoformat() + 'Z'


def convert_iso8601_to_ms(iso_date):
    # Parse the ISO 8601 date
    dt = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    # Convert to Unix timestamp in seconds and then to milliseconds
    timestamp_ms = int(dt.timestamp() * 1000)
    return timestamp_ms


def create_folder(folder):
    try:
        os.mkdir(folder)
        return f"Folder '{folder}' created successfully."
    except FileExistsError:
        return f"Folder '{folder}' already exists."