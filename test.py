import time
from datetime import datetime, timedelta
from convertdate import hebrew
from astral import LocationInfo
from astral.sun import sun
import pytz
import telebot

# =======================
# Telegram Configuration
# =======================
TELEGRAM_TOKEN = '7813630651:AAEuWgeN19Uo5kX1QVE-nrRiUSyKVJXvhZk'  # החלף את זה בטוקן שלך
CHAT_ID = '999682317'  # הכנס את ה-Chat ID שלך
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# =======================
# Location & Timezone
# =======================
LOCATION = LocationInfo("Tel Aviv", "Israel", "Asia/Jerusalem", 32.0853, 34.7818)
TIMEZONE = pytz.timezone("Asia/Jerusalem")

# =======================
# Jewish Holidays List
# =======================
JEWISH_HOLIDAYS = {
    (1, 15),  # Pesach
    (3, 6),   # Shavuot
    (7, 1),   # Rosh Hashanah
    (7, 10),  # Yom Kippur
    (7, 15),  # Sukkot
    (7, 22),  # Shemini Atzeret
    (9, 25),  # Hanukkah
}

# =======================
# Helper Functions
# =======================
def days_in_hebrew_month(year, month):
    start = hebrew.to_jd(year, month, 1)
    if month == 13:
        next_month, next_year = 1, year + 1
    elif month == 12 and not hebrew.leap(year):
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    start_next = hebrew.to_jd(next_year, next_month, 1)
    return int(round(start_next - start))

def is_eve_of_shabbat(now):
    if now.weekday() == 4:  # Friday
        s = sun(LOCATION.observer, date=now.date(), tzinfo=TIMEZONE)
        sunset = s['sunset']
        return now >= (sunset - timedelta(minutes=20))
    return False

def is_eve_of_holiday(h_year, h_month, h_day):
    days_in_month = days_in_hebrew_month(h_year, h_month)
    next_day, next_month, next_year = h_day + 1, h_month, h_year

    if next_day > days_in_month:
        next_day = 1
        if h_month == 13:
            next_month, next_year = 1, h_year + 1
        elif h_month == 12 and not hebrew.leap(h_year):
            next_month, next_year = 1, h_year + 1
        else:
            next_month += 1

    return (next_month, next_day) in JEWISH_HOLIDAYS

def wait_until_after_shabbat_or_holiday():
    global running
    now = datetime.now(TIMEZONE)
    h_year, h_month, h_day = hebrew.from_gregorian(now.year, now.month, now.day)

    if is_eve_of_shabbat(now) or is_eve_of_holiday(h_year, h_month, h_day):
        s = sun(LOCATION.observer, date=now.date(), tzinfo=TIMEZONE)
        sunset_today = s['sunset']
        next_day = now + timedelta(days=1)
        s_next = sun(LOCATION.observer, date=next_day.date(), tzinfo=TIMEZONE)
        sunset_next_day = s_next['sunset']

        start_sleep = sunset_today - timedelta(minutes=20)
        end_sleep = sunset_next_day + timedelta(minutes=15)

        if now < start_sleep:
            wait_time = (start_sleep - now).total_seconds()
            bot.send_message(CHAT_ID, f"Waiting until 20 minutes before sunset... ({wait_time / 60:.1f} minutes left)")
            time.sleep(wait_time)
            now = datetime.now(TIMEZONE)

        # Wait until after sunset the next day
        wait_time = (end_sleep - now).total_seconds()
        bot.send_message(CHAT_ID, f"Shabbat/Holiday started, resuming after sunset tomorrow.")
        time.sleep(wait_time)

        bot.send_message(CHAT_ID, "Shabbat/Holiday is over. Resuming regular execution.")

# =======================
# Telegram Bot Handlers
# =======================
@bot.message_handler(commands=['status'])
def send_status(message):
    if running:
        bot.reply_to(message, "The script is running normally.")
    else:
        bot.reply_to(message, "The script is currently paused for Shabbat or a holiday.")

# Start polling for Telegram messages
#bot.polling(none_stop=True)

# =======================
# Main Loop
# =======================
running = True
def main_loop():
    while running:
        wait_until_after_shabbat_or_holiday()
        print(f"Regular execution at {datetime.now(TIMEZONE)}")
        time.sleep(1800)  # 30 minutes

if __name__ == "__main__":
    main_loop()
