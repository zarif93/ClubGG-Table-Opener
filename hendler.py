from datetime import datetime, timedelta
import pytz
import time
import requests
from suntime import Sun, SunTimeException
from geopy.geocoders import Nominatim
from hdate import HebrewDate
import os
from dotenv import load_dotenv ,dotenv_values
import telebot

load_dotenv()
bot_token = os.getenv("TOKEN")
chat_id = os.getenv("CHAT_ID")

def chacker(mass):
    bot = telebot.TeleBot(bot_token)
    bot.send_message(chat_id, mass)

def get_date_two_weeks_ago(date_str):
    """
    מקבלת תאריך במבנה MM/DD/YYYY ומחזירה את התאריך בדיוק שבועיים אחורה.
    """
    input_date = datetime.strptime(date_str, "%m/%d/%Y")
    two_weeks_ago = input_date - timedelta(days=14)
    return two_weeks_ago.strftime("%m/%d/%Y")

def get_time_israel():
    """
    מחזירה את השעה הנוכחית בישראל (כ- string).
    """
    israel_tz = pytz.timezone('America/Mexico_City')
    now = datetime.now(israel_tz)
    return now.strftime('%m/%d/%Y')

