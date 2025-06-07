import os
import pickle
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

SESSION_FILE = os.getenv("SESSION_FILE") + ".pkl"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

def save_session_to_file(session):
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    with open(SESSION_FILE, 'wb') as f:
        pickle.dump(session.cookies, f)

def load_session_from_file():
    if not os.path.exists(SESSION_FILE):
        return None

    with open(SESSION_FILE, 'rb') as f:
        cookies = pickle.load(f)

    session = requests.Session()
    session.headers.update(HEADERS)
    for cookie in cookies:
        session.cookies.set(cookie.name, cookie.value)
    return session

def login_to_clubgg():
    print("Logging in to ClubGG...")
    username = os.getenv("CLUBUSER")
    password = os.getenv("PASSWORD")

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)  # או השמטת headless, זה ברירת מחדל
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://union.clubgg.com/login")
        # ...
        print("Navigation complete")

        print("Page content snippet:", page.content()[:500])  # הדפסת תוכן הדף ל-500 תווים

        # המשך הלוגין כמו בקוד שלך...
        page.wait_for_selector("#id")
        page.fill("#id", username)
        
        page.wait_for_selector("#pwd")
        page.fill("#pwd", password)
        
        page.click("button[onclick='postContent(this);']")
        
        page.wait_for_url("**/clublist", timeout=15000)

        cookies = context.cookies()
        session = requests.Session()
        session.headers.update(HEADERS)
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        save_session_to_file(session)
        browser.close()
        print("Login successful. Session saved.")
        return session

def is_logged_in():
    session = load_session_from_file()
    if not session:
        return login_to_clubgg()

    try:
        res = session.get("https://union.clubgg.com/clublist")
        if res.status_code == 200 and "clublist" in res.url:
            print("Still logged in.")
            return session
        else:
            print("Session expired. Logging in again...")
            return login_to_clubgg()
    except Exception as e:
        print("Error while checking login status:", e)
        return login_to_clubgg()
