from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

kbd_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kbd_menu.add("Подтвердить госпитализацию")

kbd_remove = ReplyKeyboardRemove()
