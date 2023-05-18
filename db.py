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
                    "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "current_amount FLOAT, "
                    "currency TEXT, "
                    "Дохід FLOAT, "
                    "Подорожі FLOAT, "
                    "Освіта FLOAT, "
                    "Їжа FLOAT, "
                    "Досуг FLOAT, "
                    "Авто FLOAT, "
                    "Таксі FLOAT, "
                    "`Комуналка(житло)` FLOAT, "
                    "Інше FLOAT)"
                    )
        db.commit()


async def inserting_currency(user_id, currency):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "currency"
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (currency,))
        db.commit()


async def inserting_sum_first_time(user_id, amount):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "current_amount"  # Имя целевой колонки
        cur.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE id = 1", (amount,))
        db.commit()
