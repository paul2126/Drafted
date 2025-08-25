from datetime import datetime

def _format_date(value):
    if not value:
        return None
    if isinstance(value, str):
        return value[:10]  # "YYYY-MM-DD"
    if isinstance(value, datetime):
        return value.date().isoformat()
    return value
