
from aiogram import Bot, Dispatcher, types, executor
from datetime import datetime

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
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
    await message.answer(f'Вітаю, {message.from_user.first_name}! Я допомагатиму тобі стежити за твоїми коштами.')
    await message.answer('Будь-ласка, оберіть валюту:', reply_markup=kb.currency)


class UserState(StatesGroup):
    awaiting_amount = State()


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'uah')
async def handle_amount_request(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    await bot.send_message(
        chat_id=user_id,
        text='Ви обрали UAH ₴ (Гривні). Підтвердіть Ваш вибір.',
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
        text=f'Будь-ласка, напишіть Ваші кошти станом на {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} у такому вигляді:  ****, **. Суму буде збережено як поточні кошти користувача.'
    )
    await UserState.awaiting_amount.set()
    await state.update_data(user_id=user_id)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'yes usd')
async def handle_amount_request(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    await db.inserting_currency(user_id, currency='USD')
    await bot.send_message(
        chat_id=user_id,
        text=f'Будь-ласка, напишіть Ваші кошти станом на {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} у такому вигляді:  ****, **. Суму буде збережено як поточні кошти користувача.'
    )

    await UserState.awaiting_amount.set()
    await state.update_data(user_id=user_id)


@dp.message_handler(state=UserState.awaiting_amount)
async def handle_amount(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get('user_id')

    amount = message.text

    if validate_amount_format(amount):
        await db.inserting_sum_first_time(user_id, amount)

        await message.reply(f"Ви ввели суму: {amount}. Суму збережено.")
        await state.finish()
    else:
        await message.reply("Неправильний формат суми. Введіть суму у правильному форматі.")


def validate_amount_format(amount):
    try:
        amount = float(amount.replace(",", "."))
        return round(amount, 2) == amount
    except ValueError:
        return False


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_start, skip_updates=True)
