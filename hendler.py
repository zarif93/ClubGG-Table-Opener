from datetime import datetime, timedelta
import pytz
import time
import requests
from suntime import Sun, SunTimeException
from geopy.geocoders import Nominatim
from hdate import HebrewDate

def get_last_monday(date_str):
    """
    מקבלת תאריך במבנה MM/DD/YYYY ומחזירה את יום שני האחרון שהיה (כ- string).
    """
    input_date = datetime.strptime(date_str, "%m/%d/%Y")
    last_monday = input_date - timedelta(days=(input_date.weekday() - 0) % 7)
    return last_monday.strftime("%m/%d/%Y")

def get_time_israel():
    """
    מחזירה את השעה הנוכחית בישראל (כ- string).
    """
    israel_tz = pytz.timezone('Asia/Jerusalem')
    now = datetime.now(israel_tz)
    return now.strftime('%m/%d/%Y')
