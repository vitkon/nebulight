from datetime import datetime
import pandas as pd

def to_iso_format(dt: datetime) -> str:
    return dt.isoformat()

def nanoseconds_to_iso(nanoseconds):
    # Convert nanoseconds to pandas Timestamp
    timestamp = pd.to_datetime(nanoseconds, unit='ns', utc=True)
    # Return the ISO 8601 formatted string
    return timestamp.isoformat()

def round_numeric_value(value):
    return round(value, 2)