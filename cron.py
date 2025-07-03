import requests
import pytz
import clubgg_session
from datetime import datetime, timedelta

# --- לוגיקת תאריכים חדשה ---
# קבלת התאריך של היום (יום שלישי שבו הקוד רץ)

israel_tz = pytz.timezone('America/Mexico_City')

now = datetime.now(israel_tz)

current_weekday = now.weekday()

thursday_weekday_number = 4

if current_weekday <= thursday_weekday_number:
    days_until_thursday = thursday_weekday_number - current_weekday

next_thursday = now + timedelta(days=days_until_thursday)

s_view_date_str = next_thursday.strftime("%Y-%m-%d 05:00")

saturday = next_thursday + timedelta(days=2)

e_view_date_str = saturday.strftime("%Y-%m-%d 05:00")

# --- סוף לוגיקת תאריכים חדשה ---

session = clubgg_session.is_logged_in()

url = "https://union.clubgg.com/popup_notification"

# הגדרת נתוני הטופס (Form Data)
# שימו לב: עבור שדות טקסט, נשתמש במילון 'data'.
# עבור קבצים, נשתמש במילון 'files'.
data = {
    "iam": "notice_file",
    "no": "416",
    "title": "תבש",
    "body": "",
    "s_view": s_view_date_str,
    "e_view": e_view_date_str,
    "image_yn": "1",
    "not_show_yn": "0",
    "include_clubno": "275623,87764,111381,296156,216597,298172,127103,169590,150566,28096,45461,193991,97081,",
    "imgnm": "52990674_cn_25061302_6349.jpg"
}

# הגדרת קבצים
# כיוון שהשדה 'file' בבקשה המקורית היה 'undefined',
# אנחנו נגדיר אותו כ-None או כקובץ ריק אם אין קובץ אמיתי לשלוח.
# אם יש לכם קובץ אמיתי, החליפו את 'None' ב- (שם הקובץ, תוכן הקובץ בבייטים)
files = {
    "file": (None, None) # זה מדמה את "file: undefined" - אין קובץ בפועל.
    # אם היה קובץ אמיתי, זה ייראה כך:
    # "file": ("my_image.jpg", open("path/to/my_image.jpg", "rb"))
}


# שליחת הבקשה
response = session.post(url, data=data, files=files)
