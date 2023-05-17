from aiogram import Bot, Dispatcher, types, executor

import db
import keyboards as kb
from dotenv import load_dotenv
import os

load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot)


async def on_start(_):
    await db.db_start()
    print('db started')


@dp.message_handler(commands=['start'])
async def start_bot(message: types.Message):
    await db.create_individual_table(message.chat.id, message.from_user.id)
    await message.answer_sticker('CAACAgIAAxkBAAMZZGUWOWXAyYY7LhJrZjrC7aSdn_cAAm8AA9vbfgABmVtQqHuTgHQvBA')
    await message.answer(f'Вітаю, {message.from_user.first_name}! Я - твій помічник у стеженні за коштами.')
    await message.answer('Будь-ласка, оберіть валюту:', reply_markup=kb.currency)


# unknown messages
@dp.message_handler()
async def unknown(message: types.Message):
    await message.reply('Я не розумію.')


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_start, skip_updates=True)
