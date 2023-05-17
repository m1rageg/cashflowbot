from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


currency = InlineKeyboardMarkup(row_width=2)
currency.add(InlineKeyboardButton(text='UAH ₴', callback_data='uah'),
             InlineKeyboardButton(text='USD $', callback_data='usd'),
             InlineKeyboardButton(text='UAH ₴, USD $', callback_data='uah+usd'))
