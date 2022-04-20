import logging
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.utils import exceptions

from keybords import request_phone, main_menu
from DB.hospitalization import HDB
from settings import HOSP_HOST, HOSP_PORT, HOSP_USER, HOSP_PASS, HOSP_DB


class ProfileForm(StatesGroup):
    """
    User profile
    """
    fio = State()  # ФИО
    b_y = State()  # Год рождения
    region = State()  # Регион
    phone_num = State()  # Номер телефона


async def welcome(message: Message):
    """
    Обработчик команды /start
    """
    with HDB(username=HOSP_USER,
             password=HOSP_PASS,
             host=HOSP_HOST,
             port=HOSP_PORT,
             database=HOSP_DB) as hosp_db:
        patient = hosp_db.find_patient_by_tg_user_id(message.from_user.id)
        if patient.get("pid") != -1:
            try:
                await message.answer(
                    f"Здравствуйте, {patient.get('fio')}",
                    reply_markup=main_menu.kbd_menu
                )
            except Exception as ex:
                logging.exception(ex)
        else:
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
    async with state.proxy() as data:
        data['phone_num'] = message.contact.phone_number
        with HDB(username=HOSP_USER,
                 password=HOSP_PASS,
                 host=HOSP_HOST,
                 port=HOSP_PORT,
                 database=HOSP_DB) as hosp_db:
            pid = hosp_db.find_patient(data.get('fio'), data.get('b_y'), data.get('region'), data.get('phone_num'))
            print(f"{pid=}")
            hosp_db.update_patient(pid=pid, tg_user_id=message.from_user.id)
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
