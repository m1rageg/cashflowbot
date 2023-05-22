from aiogram import Bot, Dispatcher, types, executor
from datetime import datetime
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
import db
import keyboards as kb
from dotenv import load_dotenv
import os

storage = MemoryStorage()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot,  storage=storage)
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")


async def on_start(_):
    await db.db_start()
    print('db started')


@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    await db.create_individual_table(message.chat.id, message.from_user.id)
    await message.answer_sticker('CAACAgIAAxkBAAMZZGUWOWXAyYY7LhJrZjrC7aSdn_cAAm8AA9vbfgABmVtQqHuTgHQvBA')
    await message.answer(f'Вітаю, {message.from_user.first_name}! Я допомагатиму тобі стежити за твоїми коштами.💵')
    await message.answer('💵Будь-ласка, оберіть валюту:', reply_markup=kb.currency)


class UserState(StatesGroup):
    awaiting_amount = State()


class FormStatesGroup(State):
    WAITING_FOR_AMOUNT = 1
    OTHER_STATE = 2


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'uah')
async def handle_amount_request(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await bot.send_message(
        chat_id=user_id,
        text='Ви обрали UAH ₴ (Гривні). Підтвердіть Ваш вибір.✅',
        reply_markup=kb.confirmuah
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'usd')
async def handle_amount_request(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await bot.send_message(
        chat_id=user_id,
        text='Ви обрали USD $ (Долар). Підтвердіть Ваш вибір.',
        reply_markup=kb.confirmusd
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'no')
async def handle_amount_request(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await bot.send_message(
        chat_id=user_id,
        text='Будь-ласка, оберіть валюту:',
        reply_markup=kb.currency
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'yes uah')
async def handle_amount_request(callback_query: types.CallbackQuery, state: FSMContext):

    user_id = callback_query.from_user.id
    await db.inserting_currency(user_id, currency='UAH')
    await bot.send_message(
        chat_id=user_id,
        text=f'Будь-ласка, напишіть Ваші кошти станом на {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} у такому вигляді:  ****. **. Суму буде збережено як поточні кошти користувача.'
    )
    await UserState.awaiting_amount.set()
    await state.update_data(user_id=user_id)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'yes usd')
async def handle_amount_request(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await db.inserting_currency(user_id, currency='USD')
    await bot.send_message(
        chat_id=user_id,
        text=f'Будь-ласка, напишіть Ваші кошти станом на {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} у такому вигляді:  ****. **. Суму буде збережено як поточні кошти користувача. 😉'
    )

    await UserState.awaiting_amount.set()
    await state.update_data(user_id=user_id)


@dp.message_handler(state=UserState.awaiting_amount)
async def handle_expense_amount(message: types.Message, state: FSMContext):
    try:
        amount = message.text
        if amount == 'Скасувати🚫':
            await message.answer('Ви скасували введення.', reply_markup=kb.main)
            await state.finish()
            return
        data = await state.get_data()
        category = data.get("category")
        if validate_amount_format(amount):
            if category == "food":
                await db.inserting_new_food(user_id=message.from_user.id, value=amount)
            elif category == "study":
                await db.inserting_new_study(user_id=message.from_user.id, value=amount)
            elif category == "hobby":
                await db.inserting_new_hobby(user_id=message.from_user.id, value=amount)
            elif category == "travel":
                await db.inserting_new_travel(user_id=message.from_user.id, value=amount)
            elif category == "otherexpense":
                await db.inserting_new_other(user_id=message.from_user.id, value=amount)
            elif category == "house":
                await db.inserting_new_house(user_id=message.from_user.id, value=amount)
            elif category == "car":
                await db.inserting_new_car(user_id=message.from_user.id, value=amount)
            elif category == "taxi":
                await db.inserting_new_taxi(user_id=message.from_user.id, value=amount)
            elif category == "otherincome":
                await db.inserting_new_another(user_id=message.from_user.id, value=amount)
            elif category == "award":
                await db.inserting_new_award(user_id=message.from_user.id, value=amount)
            elif category == "debt":
                await db.inserting_new_debt(user_id=message.from_user.id, value=amount)
            elif category == "income":
                await db.inserting_new_income(user_id=message.from_user.id, value=amount)
            elif category == 'credit':
                await db.loan_repayment(user_id=message.from_user.id, value=amount)
                await message.reply("✅Частину боргу успішно погашено!✅", reply_markup=kb.main)
                await state.finish()
                return
            elif category == 'creditcreate':
                await db.inserting_credit(user_id=message.from_user.id, value=amount)
                await message.reply("Кредит було додано😔", reply_markup=kb.main)
                await state.finish()
                return
            else:
                await db.inserting_sum_first_time(user_id=message.from_user.id, value=amount)

            await state.finish()
            await message.reply("✅Сума була успішно додана!✅", reply_markup=kb.main)
        else:
            raise ValueError
    except ValueError:
        await message.reply("❌ Неправильний формат суми. Введіть правильний формат. ❌")


@dp.message_handler(filters.Text(equals='Дохід💰', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="income")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви заробили(зарплата):", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Борг💸', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="debt")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви отримали у борг:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Премія🤩', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="award")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, якого розміру Ви отримали премію:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Інший дохід', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="otherincome")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть інший дохід:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='їжа🍟', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="food")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви витратили на їжу:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='освіта📚', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="study")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви витратили на освіту:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Досуг🎯', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="hobby")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви витратили на свій досуг:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Подорожі🛫', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="travel")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви витратили на подорожі:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Комуналка(житло)🏠', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="house")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви витратили на комуналку або житло:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Авто🚘', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="car")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви витратили на своє авто:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Таксі🚕', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="taxi")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви витратили на таксі:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Інша витрата', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="otherexpense")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, яку ви витратили на щось інше:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Погасити💰', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="credit")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть суму, якою Ви хочете погасити частину кредиту:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Внести розмір кредиту💸', ignore_case=True))
async def handle_food_category(message: types.Message, state: FSMContext):
    await state.update_data(category="creditcreate")
    await UserState.awaiting_amount.set()
    await message.reply("Введіть розмір Вашого кредиту:", reply_markup=kb.decline)


@dp.message_handler(filters.Text(equals='Кредит', ignore_case=True))
async def handle_nova_vitrata(message: types.Message):
    await message.answer('Оберіть дію:', reply_markup=kb.creditmenu)


@dp.message_handler(filters.Text(equals='Стан📈', ignore_case=True))
async def handle_nova_vitrata(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"Вам залишилось погасити: {await db.get_stat_by_credit(user_id)}")


@dp.message_handler(filters.Text(equals='нова витрата💸', ignore_case=True))
async def handle_nova_vitrata(message: types.Message):
    await message.answer('Будь-ласка, оберіть категорію.', reply_markup=kb.categories)


@dp.message_handler(filters.Text(equals='баланс💰', ignore_case=True))
async def handle_nova_vitrata(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"""На Вашому рахунку: {await db.getting_money(user_id)} 💵
Якщо цікаво - ось Ваша сума у доларах: {await db.convert_to_usd(user_id)}💰
Поточний курс на мінфіні складає {db.parser('https://minfin.com.ua/currency/usd/')}""")


@dp.message_handler(filters.Text(equals='новий дохід🤩', ignore_case=True))
async def handle_nova_vitrata(message: types.Message):
    await message.answer('Будь-ласка, оберіть категорію.', reply_markup=kb.categoriesplus)


@dp.message_handler(filters.Text(equals='статистика📈', ignore_case=True))
async def handle_nova_vitrata(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"""📈📈📈 Ось Ваша статистика витрат та доходів відповідно до Ваших записів. 
Сумарно Ви витратили: {await db.stat_expense(user_id)}
Сумарно Ваш дохід складає: {await db.stat_income(user_id)}""")


@dp.message_handler(filters.Text(equals='👈головне меню', ignore_case=True))
async def handle_nova_vitrata(message: types.Message):
    await message.answer('Перенаправлення на головне меню... 👈', reply_markup=kb.main)


def validate_amount_format(amount):
    try:
        amount = float(amount.replace(",", "."))
        return round(amount, 2) == amount
    except ValueError:
        return False


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_start, skip_updates=True)
