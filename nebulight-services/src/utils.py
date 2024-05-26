# src/utils.py
from datetime import datetime

def to_iso_format(dt: datetime) -> str:
    return dt.isoformat()

def remove_sensitive_fields(data: dict) -> dict:
    fields = ['owner', 'is_active']
    return {key: value for key, value in data.items() if key not in fields}