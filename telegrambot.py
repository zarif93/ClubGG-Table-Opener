import threading
import asyncio
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from clubtables import close_tables, open_missing_tables, open_more_tables, get_club_running_tables_by_game, change_table_status
from clubgg_session import is_logged_in
import os
from dotenv import load_dotenv ,dotenv_values
import ast
import telebot

load_dotenv()
bot_token = os.getenv("TOKEN")
chat_id = os.getenv("CHAT_ID")

def load_allowed_users():
    # טוען את משתני הסביבה מחדש
    load_dotenv()  # טוען את משתני הסביבה מחדש מקובץ ה- .env

    # אם אתה רוצה לקרוא את הערכים ישירות מהמילון של .env (הכי עדכני)
    config = dotenv_values(".env")
    allowed_users = config.get("ALLOWED_USERS", "")

    # אם יש ערכים ב- ALLOWED_USERS
    if allowed_users:
        return [int(user_id) for user_id in allowed_users.split(',')]
    else:
        return []  # במקרה שאין ערכים

# משתנה גלובלי שמנהל האם הלולאה פועלת
running = False

def run_open_missing_tables():
    # פונקציה רגילה שמריצה את כל הפעולות
    session = is_logged_in()
    open_missing_tables(session)

async def handle_open_missing_tables():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_open_missing_tables)

def run_open_tables():
    # פונקציה רגילה שמריצה את כל הפעולות
    session = is_logged_in()
    open_more_tables(session)

async def handle_open_tables():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_open_tables)

def run_close_tables():
    session = is_logged_in()
    close_tables(session)

async def handle_close_tables():
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, run_close_tables)

def chack_tables(state):
    session = is_logged_in()
    return get_club_running_tables_by_game(session,state)

async def handle_chack_tables(state):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: chack_tables(state))

def change_table(value):
    session = is_logged_in()
    return change_table_status(session,value)

async def handle_change_table(value):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: change_table(value))

# פונקציית הלולאה
def loop_function():
    global running
    while running:

        session = is_logged_in()
        open_missing_tables(session)

        time.sleep(1800)  # השהיה 30 דקות בין איטרציות

# כפתורים ראשיים בכניסה
def main_menu_buttons():
    keyboard = [
        #[InlineKeyboardButton("📡 הפעל בוט", callback_data='start_bot')],
        [InlineKeyboardButton("➕  פתח שולחנות חסרים" , callback_data='open_missing_tables')],
        #[InlineKeyboardButton("➕➕ פתח שולחנות", callback_data='open_tables')],
        [InlineKeyboardButton("🗑️ מחק שולחנות", callback_data='delete_tables')],
        [InlineKeyboardButton("שינוי שולחן", callback_data='get_tables')]
    ]
    return InlineKeyboardMarkup(keyboard)

# כפתורים אחרי שהבוט פועל
def active_bot_buttons():
    keyboard = [
        #[InlineKeyboardButton("⛔ עצור בוט", callback_data='stop_bot')],
        [InlineKeyboardButton("➕ פתח שולחנות חסרים" , callback_data='open_missing_tables')],
        #[InlineKeyboardButton("➕➕ פתח שולחנות", callback_data='open_tables')],
        [InlineKeyboardButton("🗑️ מחק שולחנות", callback_data='delete_tables')],
        [InlineKeyboardButton("שינוי שולחן", callback_data='get_tables')]
    ]
    return InlineKeyboardMarkup(keyboard)

def tables_menu_buttons():
    keyboard = [
        [InlineKeyboardButton("NLH", callback_data="get_table|101")],
        [InlineKeyboardButton("PLO 4", callback_data="get_table|102")],
        [InlineKeyboardButton("PLO 5", callback_data="get_table|103")],
        [InlineKeyboardButton("PLO 6", callback_data="get_table|105")],
        [InlineKeyboardButton("🔙 חזור לתפריט הראשי", callback_data="go_to_start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def change_table_buttons(value):
    
    cno, tno, rno = value.split('-')

    keyboard = [
        [InlineKeyboardButton("הצמד לראש הדף", callback_data=f"go_to_start|pin-{cno}-{tno}-{rno}")],
        [InlineKeyboardButton("בטל הצמדה", callback_data=f"go_to_start|unpin-{cno}-{tno}-{rno}")],
        [InlineKeyboardButton("מחק שולחן", callback_data=f"go_to_start|delete-{cno}-{tno}-{rno}")],
        [InlineKeyboardButton("🔙 חזור לתפריט הראשי", callback_data="go_to_start")]
    ]
    return InlineKeyboardMarkup(keyboard)

def table_menu_buttons(value):
    keyboard = []

    tables = list(value.items())
    num_tables = len(tables)
    
    # קובע את מספר השולחנות בשורה
    if num_tables > 30:
        buttons_per_row = 3
    elif num_tables > 20:
        buttons_per_row = 2
    else:
        buttons_per_row = 1

    # אוסף את השולחנות לשורות עם כפתורים
    for i in range(0, num_tables, buttons_per_row):
        row = []
        for j in range(i, min(i + buttons_per_row, num_tables)):
            table_name, table_data = tables[j]
            cno = str(table_data[0]['cno'])
            tno = str(table_data[0]['tno'])
            rno = str(table_data[0]['rno'])

            callback = f"change_table|{cno}-{tno}-{rno}"
            if len(callback) > 64:
                continue
            row.append(InlineKeyboardButton(table_name, callback_data=callback))

        keyboard.append(row)

    # כפתור חזור לתפריט הראשי
    keyboard.append([InlineKeyboardButton("🔙 חזור לתפריט הראשי", callback_data='go_to_start')])

    return InlineKeyboardMarkup(keyboard)


# התחלת הבוט / כניסה
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    allowed_users = load_allowed_users()
    chat_id = update.effective_chat.id
    print(f"Chat ID: {chat_id}")
    if update.effective_user.id not in allowed_users:
        print(update.message.from_user.id)
        await update.message.reply_text("you are not allowed to use this bot.\n"
                                        "please contact the admin.\n"
                                        "@danielkuku")
        return  # עוצר כאן אם זה לא אתה
    
    if running:
        await update.effective_message.reply_text(
            "הבוט פועל!\n\n"
            "לעצירת לחץ - עצור בוט\n"
            "לפתיחת שולחנות ידני לחץ - פתח שולחנות\n"
            "אם יש כבר שולחנות פועלים הבוט פותח עוד שולחנות \n"
            " למחיקת שולחנות לחץ - מחק שולחנות \n" 
            " אם יש 2 שולחנות עם אותו השם הבוט סוגר רק אחד מהשולחנות ",
            reply_markup=active_bot_buttons()
        )
    else:
        await update.effective_message.reply_text(
            "ברוכים הבאים לבוט פתיחת שולחנות אוטומטית!\n\n"
            "להפעלה לחץ - הפעל בוט\n"
            "לפתיחת שולחנות ידני לחץ - פתח שולחנות\n"
            "אם יש כבר שולחנות פועלים הבוט פותח עוד שולחנות \n"
            " למחיקת שולחנות לחץ - מחק שולחנות \n" 
            " אם יש 2 שולחנות עם אותו השם הבוט סוגר רק אחד מהשולחנות ",
            reply_markup=main_menu_buttons()
        )

# טיפול בכפתורים
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global running
    query = update.callback_query
    await query.answer()

    data = query.data
    if "|" in data:
        action, value = data.split("|", 1)
    else:
        action = data
        value = None
    
    if action == 'start_bot':
        if not running:
            running = True
            threading.Thread(target=loop_function).start()
        await query.edit_message_text(
            "הבוט הופעל!\n\n"
            "לעצירת לחץ - עצור בוט\n"
            "לפתיחת שולחנות ידני לחץ - פתח שולחנות\n"
            "אם יש כבר שולחנות פועלים הבוט פותח עוד שולחנות \n"
            " למחיקת שולחנות לחץ - מחק שולחנות \n" 
            " אם יש 2 שולחנות עם אותו השם הבוט סוגר רק אחד מהשולחנות ",
            reply_markup=active_bot_buttons()
        )

    elif action == 'stop_bot':
        running = False
        await query.edit_message_text(
            "הבוט נעצר!\n\n"
            "להפעלה מחדש לחץ - הפעל בוט\n"
            "לפתיחת שולחנות ידני לחץ - פתח שולחנות\n"
            "אם יש כבר שולחנות פועלים הבוט פותח עוד שולחנות \n"
            " למחיקת שולחנות לחץ - מחק שולחנות \n" 
            " אם יש 2 שולחנות עם אותו השם הבוט סוגר רק אחד מהשולחנות ",
            reply_markup=main_menu_buttons()
        )

    elif action == 'open_tables':
        # שלב 1: שולחים קודם הודעה "פותח שולחנות..."
        await query.edit_message_text(
            "פותח שולחנות... ⏳",
            reply_markup=None
        )

        # שלב 2: מריצים את הפונקציה שפותחת את השולחנות
        await handle_open_tables()

        # שלב 3: אחרי סיום, מעדכנים את ההודעה
        await query.message.edit_text(
            "פתחת שולחנות ידנית ✅",
            reply_markup=main_menu_buttons() if not running else active_bot_buttons()
        )

    elif action == 'open_missing_tables':
        running = False
        # שלב 1: שולחים קודם הודעה "פותח שולחנות..."
        await query.edit_message_text(
            "פותח שולחנות... ⏳",
            reply_markup=None
        )

        # שלב 2: מריצים את הפונקציה שפותחת את השולחנות
        await handle_open_missing_tables()

        # שלב 3: אחרי סיום, מעדכנים את ההודעה
        await query.message.edit_text(
            "פתחת שולחנות ידנית ✅",
            reply_markup=main_menu_buttons() if not running else active_bot_buttons()
        )

    elif action == 'delete_tables':
        # שלב 1: קודם שולחים הודעה שמוחקים שולחנות
        await query.edit_message_text(
            "מוחק שולחנות... ⏳",
            reply_markup=None
        )

        # שלב 2: מריצים את הפונקציה שסוגרת את השולחנות
        await handle_close_tables()

        # שלב 3: אחרי סיום, מעדכנים את ההודעה
        await query.message.edit_text(
            "✅ מחקת שולחנות ידנית!",
            reply_markup=main_menu_buttons() if not running else active_bot_buttons()
        )
    elif action == 'get_tables':

        await query.message.edit_text(
            "איזה סוג שולחן אתה רוצה לשנות?",
            reply_markup=tables_menu_buttons()
        )

    elif action == 'get_table':

        # שלב 1: קודם שולחים הודעה שמוחקים שולחנות
        await query.edit_message_text(
            "מחפש שולחנות פעילים ... ⏳",
            reply_markup=None
        )


        tables = await handle_chack_tables(value)


        await query.message.edit_text(
            "איזה שולחן אתה רוצה לשנות?",
            reply_markup=table_menu_buttons(tables)
        )

    elif action == 'change_table':

        await query.message.edit_text(
            "מה תרצה לשנות ?",
            reply_markup=change_table_buttons(value)
        )  

    elif action == "go_to_start":

        if value:
            await handle_change_table(value)

        await start(update, context)  # פשוט מפעיל את start מחדש
        return


# יצירת הבוט
app = ApplicationBuilder().token(bot_token).build()

# חיבור הפקודות
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))

# הפעלת הבוט
print("Starting bot...")
app.run_polling()
