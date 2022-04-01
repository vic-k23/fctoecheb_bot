import logging
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.utils import exceptions

from keybords import request_phone, main_menu


class ProfileForm(StatesGroup):
    """
    User profile
    """
    fio = State()  # ФИО
    b_y = State()  # Год рождения
    region = State()  # Регион
    phone_num = State()  # Номер телефона


async def welcome(message: Message):
    # Set profile state
    await ProfileForm.fio.set()

    # Send welcome message
    await message.reply("Здравствуйте! Давайте познакомимся. \n"
                        "Напишите, пожалуйста, свои \n"
                        "Фамилию Имя Отчество \n"
                        "(строго в этом порядке, иначе мы не подружимся :-( )")


async def process_fio(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['fio'] = message.text

    await ProfileForm.next()
    await message.reply("Какого вы года рождения?")


async def process_birth_year(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['b_y'] = message.text

    await ProfileForm.next()
    await message.reply("Из какого вы региона?")


async def process_region(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['region'] = message.text

    await ProfileForm.next()

    await message.reply("Сообщите, пожалуйста, ваш номер телефона, нажав кнопку ниже", reply_markup=request_phone.kbd)


async def process_phone_number(message: Message, state: FSMContext):
    print('=' * 20)
    async with state.proxy() as data:
        data['phone_num'] = message.contact.phone_number
    try:
        await message.reply(
            f"Приятно познакомиться",
            reply_markup=main_menu.kbd_menu
        )
    except Exception as ex:
        logging.exception(ex)
    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(welcome, commands='start')
    dp.register_message_handler(process_fio, state=ProfileForm.fio)
    dp.register_message_handler(process_birth_year, state=ProfileForm.b_y)
    dp.register_message_handler(process_region, state=ProfileForm.region)
    dp.register_message_handler(process_phone_number, content_types=ContentType.CONTACT, state=ProfileForm.phone_num)
