import sqlite3
import requests
from bs4 import BeautifulSoup as bs

db = sqlite3.connect('bot.db')
cur = db.cursor()
url = 'https://minfin.com.ua/currency/usd/'


def parser(url):
    req = requests.get(url)
    soup = bs(req.text, 'html.parser')
    usd = soup.find('div', class_='sc-1x32wa2-9 bKmKjX')
    res = usd.text[:-4].replace(',', '.')
    return res


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
                    "Борг FLOAT, "
                    "Премія FLOAT, "
                    "ІншийДохід FLOAT,"
                    "Подорожі FLOAT, "
                    "Освіта FLOAT, "
                    "Їжа FLOAT, "
                    "Досуг FLOAT, "
                    "Авто FLOAT, "
                    "Таксі FLOAT, "
                    "Комуналка FLOAT, "
                    "ІншаВитрата FLOAT,"
                    "Кредит FLOAT,"
                    "Погашено FLOAT)"
                    )
        db.commit()


async def inserting_credit(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        if ',' in str(value):
            value = str(value)
            value = float(value.replace(',', '.'))
        column_name = "Кредит"  # Имя целевой колонки
        cur.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE id = 1", (value,))
        db.commit()


async def loan_repayment(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Погашено"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        query1 = f"UPDATE {table_name} SET Кредит = Кредит - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        cur.execute(query1, parameters)
        db.commit()


async def get_stat_by_credit(user_id):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT Кредит FROM {table_name} WHERE id = 1;")
    result = cur.fetchone()
    if result is not None:
        value = result[0]
        return value if value > 0 else 0


async def convert_to_usd(user_id):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT current_amount FROM {table_name} WHERE id = 1;")
    result = cur.fetchone()
    if result is not None:
        value = result[0]
        res = value / float(parser(url))
        return round(res, 2)


async def inserting_currency(user_id, currency):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "currency"
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (currency,))
        db.commit()


async def inserting_sum_first_time(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        if ',' in str(value):
            value = str(value)
            value = float(value.replace(',', '.'))
        column_name = "current_amount"  # Имя целевой колонки
        cur.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE id = 1", (value,))
        db.commit()


async def getting_money(user_id):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT current_amount FROM {table_name} WHERE id = 1;")
    result = cur.fetchone()
    if result is not None:
        value = result[0]
        return round(value, 2)


async def stat_expense(user_id):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT SUM(Їжа), SUM(Досуг), SUM(Авто), SUM(Освіта), SUM(Подорожі), SUM(ІншаВитрата), SUM(Таксі), SUM(Комуналка) FROM {table_name};")
    result = cur.fetchone()
    if result:
        total_food = result[0] if result[0] is not None else 0
        total_hobby = result[1] if result[1] is not None else 0
        total_car = result[2] if result[2] is not None else 0
        total_study = result[3] if result[3] is not None else 0
        total_travel = result[4] if result[4] is not None else 0
        total_other = result[5] if result[5] is not None else 0
        total_taxi = result[6] if result[6] is not None else 0
        total_house = result[7] if result[7] is not None else 0
        total = total_food + total_house + total_taxi + total_other + total_travel + total_study + total_car + total_hobby
        return total


async def stat_income(user_id):
    table_name = f"user_categories_{user_id}"
    cur.execute(
        f"SELECT SUM(Премія), SUM(Дохід), SUM(ІншийДохід), SUM(Борг) FROM {table_name};")
    result = cur.fetchone()
    if result:
        total_award = result[0] if result[0] is not None else 0
        total_income = result[1] if result[1] is not None else 0
        total_other = result[2] if result[2] is not None else 0
        total_debt = result[3] if result[3] is not None else 0
        total = total_debt + total_income + total_award + total_other
        return total


async def inserting_new_income(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Дохід"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount + ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_debt(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Борг"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount + ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_award(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Премія"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount + ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_another(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "ІншийДохід"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount + ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_other(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "ІншаВитрата"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_food(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Їжа"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_study(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Освіта"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_travel(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Подорожі"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_car(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Авто"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_taxi(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Таксі"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_house(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Комуналка"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()


async def inserting_new_hobby(user_id, value):
    table_name = f"user_categories_{user_id}"
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    existing_table = cur.fetchone()
    if existing_table:
        column_name = "Досуг"  # Имя целевой колонки
        cur.execute(f"INSERT INTO {table_name} ({column_name}) VALUES (?)", (value,))
        query = f"UPDATE {table_name} SET current_amount = current_amount - ? WHERE id = ?;"
        parameters = (value, 1)
        cur.execute(query, parameters)
        db.commit()
