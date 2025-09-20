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

def add_club_to_env(club_name, value, env_file=".env"):
    """
    מוסיף קלאב ל-ENV עם הערך הנתון (ללא גרשים)
    value צריך להיות מחרוזת כמו: "60.0,50.0"
    """
    club_name = club_name.replace(" ", "")
    value = value.replace("'", "").replace('"', "")  # הסרת גרשים אם יש

    # עדכון או הוספת הקלאב בקובץ
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()

        with open(env_file, "w") as f:
            found = False
            for line in lines:
                if line.startswith(f"{club_name}="):
                    f.write(f"{club_name}={value}\n")
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(f"{club_name}={value}\n")
    else:
        with open(env_file, "w") as f:
            f.write(f"{club_name}={value}\n")

    # עדכון בזמן ריצה
    os.environ[club_name] = value
    """
    מוסיף קלאב לרשימת ALL_CLUBS בקובץ ENV בלי כפילויות
    """
    club_name = club_name.replace(" ", "")

    # טען את הקיים
    all_clubs_str = os.getenv("ALL_CLUBS", "")
    all_clubs = all_clubs_str.split(",") if all_clubs_str else []

    # הוסף את הקלאב אם הוא לא קיים
    if club_name not in all_clubs:
        all_clubs.append(club_name)

    # כתוב מחדש את השורה ALL_CLUBS בקובץ ENV
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            lines = f.readlines()

        with open(env_file, "w") as f:
            found = False
            for line in lines:
                if line.startswith("ALL_CLUBS="):
                    f.write(f"ALL_CLUBS={','.join(all_clubs)}\n")
                    found = True
                else:
                    f.write(line)
            if not found:
                f.write(f"ALL_CLUBS={','.join(all_clubs)}\n")
    else:
        # אם הקובץ לא קיים, צור אותו עם השורה
        with open(env_file, "w") as f:
            f.write(f"ALL_CLUBS={','.join(all_clubs)}\n")

    # עדכון בזמן ריצה
    os.environ["ALL_CLUBS"] = ",".join(all_clubs)