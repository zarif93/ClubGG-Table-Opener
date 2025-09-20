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

## get two weeks ago
def get_last_monday(date_str):
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

def get_last_monday_and_week(date_str: str) -> tuple[str, str]:
    """
    מקבלת תאריך במבנה MM/DD/YYYY ומחזירה את יום שני האחרון
    ואת התאריך 7 ימים לאחר מכן (סוף השבוע).
    """
    input_date = datetime.strptime(date_str, "%m/%d/%Y")
    days_since_monday = input_date.weekday()  # 0=Monday
    last_monday = input_date - timedelta(days=days_since_monday)
    week_end = last_monday + timedelta(days=6)

    return last_monday.strftime("%m/%d/%Y"), week_end.strftime("%m/%d/%Y")

def add_to_env_file(key, value, filename=".env"):
    line = f"{key}={value}\n"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(line)

def add_club_to_all_clubs(club_name, env_file=".env"):
    club_name = club_name.replace(" ", "")

    # אם הקובץ לא קיים – צור אותו עם הקלאב
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write(f"ALL_CLUBS={club_name}\n")
        os.environ["ALL_CLUBS"] = club_name
        return

    # קרא את תוכן הקובץ
    with open(env_file, "r") as f:
        lines = f.readlines()

    all_clubs = []
    found = False

    for line in lines:
        if line.startswith("ALL_CLUBS="):
            all_clubs = line.strip().split("=")[1].split(",") if line.strip().split("=")[1] else []
            found = True
            break

    # אם הקלאב כבר קיים – לא צריך לעדכן
    if club_name in all_clubs:
        return

    # הוסף את הקלאב לרשימה
    all_clubs.append(club_name)

    # כתוב מחדש
    with open(env_file, "w") as f:
        updated = False
        for line in lines:
            if line.startswith("ALL_CLUBS="):
                f.write(f"ALL_CLUBS={','.join(all_clubs)}\n")
                updated = True
            else:
                f.write(line)
        if not updated:
            f.write(f"ALL_CLUBS={','.join(all_clubs)}\n")

    # עדכון בזמן ריצה
    os.environ["ALL_CLUBS"] = ",".join(all_clubs)