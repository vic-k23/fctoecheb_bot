from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove

# Configure ReplyKeyboardMarkup
kbd = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
kbd.add("Да", "Нет")

kbd_remove = ReplyKeyboardRemove()
