from clubgg_session import is_logged_in
from hendler import get_last_monday, get_time_israel
from datetime import datetime, timedelta
import requests
import time
from hendler import chacker

delay = 3

def get_club_templates(session):
    template = {}
    
    # מעבר על סוגי המשחקים 3, 2, 1
    for gameytpe in range(3, 0, -1):
        data = {
            "iam": "list",
            "gtype": gameytpe,
            "cur_page": "1"
        }

        response = session.post("https://union.clubgg.com/template", data=data)
        
        if response.status_code == 200:
            response_data = response.json()
            
            if response_data.get('DATA') and response_data['PAGE'].get('tot_pages', 0) > 0:
                totpage = response_data['PAGE']['tot_pages']
                
                for curpage in range(totpage, 0, -1):
                    data = {
                        "iam": "list",
                        "gtype": gameytpe,
                        "cur_page": curpage
                    }
                    response = session.post("https://union.clubgg.com/template", data=data)

                    if response.status_code == 200:
                        page_data = response.json()
                        
                        for game in page_data.get('DATA', []):
                            key = f"{game['f3']}_{game['f4']}"
                            if key not in template:
                                template[key] = []

                            template[key].append({
                                "sino": game['sino'],
                                "tplno": game['tplno']
                            })
                        print(f"✅ Fetched page {curpage} for game type {gameytpe}")
                    else:
                        print(f"❌ Error fetching data for page {curpage}")
                    
                    # המתנה של 5 שניות בין בקשות
                    time.sleep(delay)
        else:
            print(f"❌ Error fetching data for game type {gameytpe}")
        
        # המתנה של 5 שניות בין סוגי משחקים
        time.sleep(delay)

    return template

def get_club_running_tables(session):
    runingtable = {}
    today = get_time_israel()
    states = ["2", "3"]

    for state in states:
        data = {
            "iam": "list",
            "from": get_last_monday(today),
            "to": today,
            "type": "2",
            "game": "0",
            "state": state,
            "blindstr": "0",
            "cur_page": "1",
            "table_name": "",
            "generate_type": "0"
        }

        response = session.post("https://union.clubgg.com/ringlist", data=data)
        
        if response.status_code == 200:
            response_data = response.json()
            totpage = response_data['PAGE'].get('tot_pages', 0)

            for curpage in range(totpage, 0, -1):
                data['cur_page'] = str(curpage)
                response = session.post("https://union.clubgg.com/ringlist", data=data)

                if response.status_code == 200:
                    page_data = response.json()

                    for game in page_data.get('DATA', []):
                        if game['f8'] in ["Not Started", "In Progress"]:
                            key = f"{game['f4']}_{game['f5']}"
                            if key not in runingtable:
                                runingtable[key] = []

                            runingtable[key].append({
                                "sino": game['cno'],
                                "tplno": game['tno']
                            })
                    print(f"✅ Fetched page {curpage} for state {state}")
                else:
                    print(f"❌ Error fetching data for page {curpage}")
                
                # המתנה של 5 שניות בין בקשות
                time.sleep(delay)
        else:
            print(f"❌ Error fetching data for state {state}")
        
        # המתנה של 5 שניות בין סוגי סטייט
        time.sleep(delay)

    return runingtable

def get_club_running_tables_by_game(session, game):
    """
    מביא את כל השולחנות הפעילים לפי סוג המשחק.
    game צריך להיות אחד מ: 101 NLH, 102 PLO, 103 PLO5, 105 PLO6
    """
    running_table = {}
    today = get_time_israel()
    states = ["2", "3"]

    for state in states:
        # קריאה ראשונה כדי לבדוק כמה עמודים יש
        data = {
            "iam": "list",
            "from": get_last_monday(today),
            "to": today,
            "type": "2",
            "game": game,
            "state": state,
            "blindstr": "0",
            "cur_page": "1",
            "table_name": "",
            "generate_type": "0"
        }

        response = session.post("https://union.clubgg.com/ringlist", data=data)

        if response.status_code == 200:
            try:
                response_data = response.json()
                totpage = int(response_data['PAGE'].get('tot_pages', 1))
                print(f"🗂️ Total Pages for game {game} (state {state}): {totpage}")

                # לולאה על כל העמודים
                for curpage in range(1, totpage + 1):
                    data["cur_page"] = str(curpage)
                    response = session.post("https://union.clubgg.com/ringlist", data=data)

                    if response.status_code == 200:
                        try:
                            response_data = response.json()
                            for game_data in response_data.get('DATA', []):
                                if game_data['f8'] in ["Not Started", "In Progress"]:
                                    key = f"{game_data['f4']}_{game_data['f5']}"
                                    if key not in running_table:
                                        running_table[key] = []
                                    running_table[key].append({
                                        "cno": game_data['cno'],
                                        "tno": game_data['tno'],
                                        "rno": game_data['rno']
                                    })
                            print(f"✅ Fetched page {curpage} for state {state}")
                        except ValueError:
                            print(f"❌ Error parsing JSON on page {curpage}")
                    else:
                        print(f"❌ Error fetching data for page {curpage}: {response.status_code}")

                    time.sleep(delay)  # השהייה בין בקשות
            except ValueError:
                print(f"❌ Error parsing initial JSON response for game {game}")
        else:
            print(f"❌ Error fetching initial data for game {game}: {response.status_code}")

    return running_table

def open_missing_tables(session):
    # שליפת תבניות ושולחנות פעילים
    template = get_club_templates(session)
    running_table = get_club_running_tables(session)

    # מציאת מפתחות משותפים והסרתם מהרשימות
    common_keys = set(template.keys()) & set(running_table.keys())
    for key in common_keys:
        template.pop(key, None)
        running_table.pop(key, None)

    # בניית מחרוזת לפתיחת שולחנות חסרים
    tpl_list = [f"{t['tplno']},{t['sino']},1" for games in template.values() for t in games]
    tpl_str = "|".join(tpl_list)

    # בקשת POST לפתיחת שולחנות
    if tpl_str:
        data = {
            "iam": "create_rg_many",
            "tplstr": tpl_str
        }
        response = session.post("https://union.clubgg.com/template", data=data)
        
        if response.status_code == 200:
            print("✅ Missing tables opened successfully.")
        else:
            print(f"❌ Error opening tables: {response.status_code}")
    else:
        print("🔎 No missing tables found to open.")

    print("🟢 end open missing tables")

def close_tables(session):

    # cancel all recurring tables
    recurring_tables(session)

    running_table = get_club_running_tables(session)

    for game, tables in running_table.items():
        # בדיקה אם הרשימה קיימת ואינה ריקה
        if tables and isinstance(tables, list):
            for index, table in enumerate(tables):
                # בדיקה אם המפתחות קיימים
                if 'sino' in table and 'tplno' in table:
                    data = {
                        "iam": "disband",
                        "cno": table['sino'],
                        "tno": table['tplno']
                    }
                    
                    response = session.post("https://union.clubgg.com/ringinfo", data=data)
                    time.sleep(delay)

                    # בדיקה אם הבקשה הצליחה
                    if response.status_code == 200:
                        print(f"✔️  Closed table '{game}' (Index {index}) successfully. (sino: {table['sino']}, tplno: {table['tplno']})")
                        chacker(f"Closed table '{game}' (Index {index}) successfully. (sino: {table['sino']}, tplno: {table['tplno']})")
                    else:
                        print(f"❌  Failed to close table '{game}' (Index {index}). Status: {response.status_code}")
                        chacker(f"Failed to close table '{game}' (Index {index}). Status: {response.status_code}")
                else:
                    print(f"⚠️  Missing data for table '{game}' at index {index}")
        else:
            print(f"⚠️  Data not found or incomplete for table '{game}'")

def open_more_tables(session):
    """
    פותח שולחנות מכל התבניות שקיימות במערכת.
    """
    # שליפת תבניות מהמערכת
    template = get_club_templates(session)

    # בניית מחרוזת לפתיחת שולחנות (לוקח את כולם, לא רק את הראשון בכל מפתח)
    tpl_list = [f"{t['tplno']},{t['sino']},1" for games in template.values() for t in games]
    tpl_str = "|".join(tpl_list)

    if tpl_str:
        data = {
            "iam": "create_rg_many",
            "tplstr": tpl_str
        }
        
        # שליחת הבקשה לפתיחת השולחנות
        response = session.post("https://union.clubgg.com/template", data=data)
        
        if response.status_code == 200:
            print("✅ All tables opened successfully.")
        else:
            print(f"❌ Error opening tables: {response.status_code}")
    else:
        print("🔎 No tables found to open.")

    print("🟢 end open more tables")

def change_table_status(session, data):
    try:
        print(f"Processing: {data}")
        act, cno, tno, rno = data.split('-')
    except ValueError:
        print("❌ Invalid data format. Expected 'action-cno-tno-rno'")
        return False

    payload = {
        "cno": cno,
        "tno": tno,
        "rno": rno
    }

    if act == "delete":
        payload["iam"] = "disband"
        response = session.post("https://union.clubgg.com/ringinfo", data=payload)
    elif act == "pin":
        payload.update({
            "iam": "pintothetop",
            "pinyn": "1"
        })
        response = session.post("https://union.clubgg.com/ringinfo", data=payload)
    elif act == "unpin":
        payload.update({
            "iam": "pintothetop",
            "pinyn": "0"
        })
        response = session.post("https://union.clubgg.com/ringinfo", data=payload)
    else:
        print(f"❌ Unknown action: {act}")
        return False

    if response.status_code == 200:
        print(f"✅ Action '{act}' successful.")
        return True
    else:
        print(f"❌ Failed to perform '{act}', status code: {response.status_code}")
        return False

def recurring_tables(session):

    data = {
        "iam": "list",
        "gtype": "1",
        "game": "0",
        "recurring_yn": "99", 
        "cur_page": "1"
    }
    response = session.post("https://union.clubgg.com/recurring", data=data)
    
    if response.status_code == 200:
        response_data = response.json()
        
        if response_data.get('DATA') and response_data['PAGE'].get('tot_pages', 0) > 0:
            totpage = response_data['PAGE']['tot_pages']
            
            for curpage in range(totpage, 0, -1):
                data = {
                    "iam": "list",
                    "gtype": "1",
                    "game": "0",
                    "recurring_yn": "99", 
                    "cur_page": curpage
                }
                response = session.post("https://union.clubgg.com/recurring", data=data)

                if response.status_code == 200:
                    page_data = response.json()

                    for game in page_data.get('DATA', []):
                            
                            data = {
                                "iam": "onoff",
                                "sino": game['sino'],
                                "rec_no": game['rec_no'],
                                "gtype": "1",
                                "onoff": "1"  # או "0" אם רוצים לכבות את
                            }

                            response = session.post("https://union.clubgg.com/recurring", data=data)

                            data = {
                                "iam": "delete",
                                "sino": game['sino'],
                                "rec_no": game['rec_no'],
                                "onoff": "0"  # או "0" אם רוצים לכבות את
                            }

                            response = session.post("https://union.clubgg.com/recurring", data=data)
                            if response.status_code == 200:
                                print(f"✅ Processed recurring table: {game['sino']}")
                                chacker(f"Processed recurring table: {game['sino']}")
                            else:
                                print(f"❌ Error processing recurring table: {game['sino']}")
                                chacker(f"Error processing recurring table: {game['sino']}")
                         
                            time.sleep(delay)
                    
                else:
                    print(f"❌ Error fetching data for page {curpage}")
    else:
        print(f"❌ Error fetching data for game type ")

