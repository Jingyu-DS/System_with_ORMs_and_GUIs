import calendar
from datetime import datetime

def get_last_day_of_month(latest_date: str):
    """
    This function is used to get the last day of the month. The month is the month of the latest transaction in the current anout
    """
    date_obj = datetime.strptime(latest_date, "%Y-%m-%d")
    _, last_day = calendar.monthrange(date_obj.year, date_obj.month)
    return datetime(date_obj.year, date_obj.month, last_day).strftime("%Y-%m-%d")


def validate_date(date_str):
    """Check if the entered date follows YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False