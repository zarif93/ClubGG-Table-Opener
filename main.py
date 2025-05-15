from clubgg_session import login_to_clubgg, is_logged_in
from clubtables import get_club_templates
from datetime import datetime, timedelta
import requests
import time

# get all running tables
#get_club_templates(session)

#close all the tables
#close_tables(session)

# open new tables 
#open_missing_tables(session)

#open new tables
#open_more_tables(session)


def main():
    session = is_logged_in()
    if session:
        while True:
            try:
                response = session.get("https://union.clubgg.com/clublist")
                if response.status_code == 200 and "clublist" in response.url:
                    get_club_templates(session)
                    print("Session is valid!", response.url)
                    tur_table(session)
                else:
                    print("Session is invalid, logging in again...")
                    session = login_to_clubgg()
            except Exception as e:
                print("Error during session check or data fetch:", e)
                session = login_to_clubgg()

            time.sleep(1800)  # 30 דקות הפסקה בין מחזורים
    else:
        print("Failed to log in or validate session.")

def tur_table(session):

    start_date = datetime.now()

    games = {
        "plo": "41041,202",
        "nlh": "41043,201",
    }

    for game in games:

        if game == "plo":
            x = 11
            y = 7

        if game == "nlh":
            x = 4
            y = 0

        for i in range(5):  # לדוגמה 5 ימים
            next_day = start_date + timedelta(days=i)
            startdt = next_day.replace(hour=x , minute=0, second=0, microsecond=0)
            startdt_register = next_day.replace(hour=y, minute=0, second=0, microsecond=0)

            data = {
                "iam": "create_mtt",
                "tplno": f"{games[game]}",
                "startdt": f"{startdt.strftime('%m/%d/%Y %H:%M:%S')}",
                "startdt_register": f"{startdt_register.strftime('%m/%d/%Y %H:%M:%S')}",
            }

            response = session.post("https://union.clubgg.com/template", data=data)
            time.sleep(10)

    print("סטטוס קוד:", response.status_code)

    

if __name__ == "__main__":
    #session = is_logged_in()
    #tur_table(session)
    pass
