import requests
import time
from clubgg_session import is_logged_in




def nlh_turnament(session, url, dates):


    for date in dates:  

        data = {
            "iam": "create_mtt",
            "tplno": "41043,201",
            "startdt": f"05/{date}/2025 04:00:00",
            "startdt_register": f"05/{date}/2025 00:00:00",
        }
        response = session.post(url, data=data)

        print("סטטוס קוד:", response.status_code)
        print("תוכן התגובה:", response.text)

        time.sleep(10)


def plo_turnament(session, url, dates):

    

    for date in dates:  

        print("date:", date)

        data = {
            "iam": "create_mtt",
            "tplno": "41041,202",
            "startdt": f"05/{date}/2025 11:00:00",
            "startdt_register": f"05/{date}/2025 07:00:00",
        }
        response = session.post(url, data=data)

        print("סטטוס קוד:", response.status_code)
        print("תוכן התגובה:", response.text)

        time.sleep(10)

#session = is_logged_in()

dates = ["04", "05", "06", "07", "08"]

url = "https://union.clubgg.com/template"

#plo_turnament(session, url, dates)

#nlh_turnament(session, url, dates)