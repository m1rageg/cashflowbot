from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


currency = InlineKeyboardMarkup(row_width=2)
currency.add(InlineKeyboardButton(text='UAH ₴', callback_data='uah'),
             InlineKeyboardButton(text='USD $', callback_data='usd'))


confirmuah = InlineKeyboardMarkup(row_width=1)
confirmuah.add(InlineKeyboardButton(text='Так', callback_data='yes uah'),
            InlineKeyboardButton(text='Ні, обрати ще раз', callback_data='no'))


confirmusd = InlineKeyboardMarkup(row_width=1)
confirmusd.add(InlineKeyboardButton(text='Так', callback_data='yes usd'),
            InlineKeyboardButton(text='Ні, обрати ще раз', callback_data='no'))

