import os
import pickle
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

SESSION_FILE = os.getenv("SESSION_FILE") + ".pkl"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',

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
    print("🔐 Logging in to ClubGG...")
    username = os.getenv("CLUBUSER")
    password = os.getenv("PASSWORD")

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True, slow_mo=100)  # DEBUG MODE
        context = browser.new_context()
        page = context.new_page()
        page.set_extra_http_headers(HEADERS)

        try:
            print("🔄 Going to login page...")
            page.goto("https://union.clubgg.com/login", timeout=60000)
        except Exception as e:
            print("❌ Failed to load login page:", e)
            browser.close()
            raise

        try:
            page.wait_for_selector("#id", timeout=10000)
            page.fill("#id", username)
            page.wait_for_selector("#pwd", timeout=10000)
            page.fill("#pwd", password)
            page.click("button[onclick='postContent(this);']")
        except Exception as e:
            print("❌ Failed during form interaction:", e)
            browser.close()
            raise

        try:
            print("⏳ Waiting for clublist URL...")
            page.wait_for_url("**/clublist", timeout=60000)  # more time
        except Exception as e:
            print("❌ Timeout waiting for clublist page:", e)
            print("🌐 Current URL:", page.url)
            page.screenshot(path="login_fail.png")
            browser.close()
            raise

        print("✅ Login successful. Saving session.")
        cookies = context.cookies()
        session = requests.Session()
        session.headers.update(HEADERS)
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        save_session_to_file(session)
        browser.close()
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
