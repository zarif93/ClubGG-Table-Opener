from clubgg_session import is_logged_in
from datetime import datetime

login = is_logged_in()



# Get 
def get_players_data(session):

    url = "https://union.clubgg.com/"

    data = {
        "iam" : "list",
        "mtypestr" : 0,
        "clubstr" : 0,
        "cur_page" : 1,
        "column" : "lastplay",
        "asc" : 2
    }

    response = session.post(f"{url}memberlist", data=data)

    print(response.json())
    
    user_id = response.json()["DATA"][0]["f2"]
    username = response.json()["DATA"][0]["f2"]
    club = response.json()["DATA"][0]["f3"]
    role = response.json()["DATA"][0]["f4"]
    rake = response.json()["DATA"][0]["f9"]
    winlose = response.json()["DATA"][0]["f11"]

    data = {
        "iam" : "set",
        "memberno" : response.json()["DATA"][0]["uno"],
        "memberclub" : response.json()["DATA"][0]["cno"]
    }

    response = session.post(f"{url}memberinfo", data=data)

    data = {
        "iam" : "info",
        "from" : "05/12/2025",
        "to" : "05/19/2025",
        "game" : 0
    }

    response = session.post(f"{url}memberinfo", data=data)

    #print(response.json()["INFO"])

    super_agent = response.json()["INFO"]["superagent"]
    agent = response.json()["INFO"]["agent"]

    all_user_data = {
        "club" : club,
        "super_agent" : super_agent,
        "agent" : agent,
        "user_id" : user_id,
        "username" : username,
        "role" : role,
        "rake" : rake,
        "winlose" : winlose
    }

    #print(all_user_data)



get_players_data(login)