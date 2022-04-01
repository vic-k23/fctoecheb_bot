from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

kbd_btn = KeyboardButton("Отправить номер телефона", request_contact=True)
kbd = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
kbd.add(kbd_btn)
