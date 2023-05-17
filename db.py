import sqlite3

db = sqlite3.connect('bot.db')
cur = db.cursor()


async def db_start():
    cur.execute("CREATE TABLE IF NOT EXISTS wallet("
                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                "tg_id INTEGER)")
    db.commit()


async def create_individual_table(chat_id, user_id):
    user = cur.execute("SELECT * FROM wallet WHERE tg_id=={key}".format(key=user_id)).fetchone()
    if not user:
        cur.execute("INSERT INTO wallet (tg_id) VALUES({key})".format(key=user_id))
        cur.execute(f"CREATE TABLE IF NOT EXISTS user_categories_{chat_id} ("
                    "current_amount FLOAT,"
                    "currency TEXT" 
                    "Їжа FLOAT,"
                    "Досуг FLOAT,"
                    "Авто FLOAT,"
                    "Комуналка FLOAT)")
        db.commit()
