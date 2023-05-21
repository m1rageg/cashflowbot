from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


currency = InlineKeyboardMarkup(row_width=2)
currency.add(InlineKeyboardButton(text='UAH ₴', callback_data='uah'),
             InlineKeyboardButton(text='USD $', callback_data='usd'))

confirmuah = InlineKeyboardMarkup(row_width=2)
confirmuah.add(InlineKeyboardButton(text='Так', callback_data='yes uah'),
            InlineKeyboardButton(text='Ні, обрати ще раз', callback_data='no'))

confirmusd = InlineKeyboardMarkup(row_width=1)
confirmusd.add(InlineKeyboardButton(text='Так', callback_data='yes usd'),
            InlineKeyboardButton(text='Ні, обрати ще раз', callback_data='no'))

main = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
main.row('Баланс💰', 'Статистика📈')
main.row('Нова витрата💸', 'Новий дохід🤩')
main.row('Кредит')

categories = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
categories.row('Їжа🍟','Досуг🎯')
categories.row('Подорожі🛫','Освіта📚')
categories.row('Комуналка(житло)🏠','Авто🚘')
categories.row('Таксі🚕','Інша витрата')
categories.row('👈Головне меню')

categoriesplus = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
categoriesplus.row('Дохід💰','Борг💸')
categoriesplus.row('Премія🤩','Інший дохід')
categoriesplus.row('👈Головне меню')

decline = ReplyKeyboardMarkup(row_width=1)
decline.add('Скасувати🚫')

creditmenu = ReplyKeyboardMarkup(resize_keyboard=True)
creditmenu.row("Внести розмір кредиту💸", 'Погасити💰', 'Стан📈')
creditmenu.row('👈Головне меню')