import logging
from locale import getlocale, setlocale, LC_ALL
from datetime import date
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from DB.hospitalization import HDB
from keybords import yes_no
from settings import HOSP_DB, HOSP_HOST, HOSP_PASS, HOSP_PORT, HOSP_USER


class PollForm(StatesGroup):
    """
    Object for poll results
    """
    hosp_id = State()  # ID записи госпитализации, которую можно подтвердить
    is_confirmed = State()  # Подтверждение госпитализации
    reason = State()  # Причина, по которой пациент не сможет приехать, если такое случится


async def start_confirmation_poll(message: Message, state: FSMContext):
    """
    This handler will be called when user sends `Подтвердить госпитализацию` command.
    """
    try:
        with HDB(username=HOSP_USER,
                 password=HOSP_PASS,
                 host=HOSP_HOST,
                 port=HOSP_PORT,
                 database=HOSP_DB) as hosp_db:
            patient = hosp_db.find_patient_by_tg_user_id(message.from_user.id)
            hospitalizations = hosp_db.find_patient_hospitalizations(patient.get('pid'))
            for_confirm = None
            if len(hospitalizations) > 0:
                for hospitalization in hospitalizations:
                    if (hospitalization.get("hosp_date") - date.today()).days > 0:
                        for_confirm = hospitalization
                        break
            if for_confirm is not None:
                async with state.proxy() as data:
                    data['hosp_id'] = for_confirm.get('hosp_id')
                    await PollForm.is_confirmed.set()
                current_locale = getlocale()
                setlocale(LC_ALL, 'ru_RU')
                text = f"Подтверждаете ли вы своё прибыте на госпитализацию " \
                       f"к {date.strftime(for_confirm.get('hosp_date'), '%a, %d %b %Y')}?"
                await message.reply(text, reply_markup=yes_no.kbd)
                setlocale(LC_ALL, current_locale)
            else:
                await message.answer("У вас нет предстоящих госпитализаций.")
    except Exception as ex:
        logging.exception(ex)


async def process_confirmation(message: Message, state: FSMContext):
    """
    Process conformation of hospitalization
    """
    async with state.proxy() as data:
        if message.text == "Да":
            await message.reply(
                "Благодарим за подтверждение!",
                reply_markup=yes_no.kbd_remove
            )
            with HDB(username=HOSP_USER,
                     password=HOSP_PASS,
                     host=HOSP_HOST,
                     port=HOSP_PORT,
                     database=HOSP_DB) as hosp_db:
                hosp_db.update_hospitalization(data.get('hosp_id'), True)
            await state.finish()
        else:
            data['confirmation'] = "Нет"
            await PollForm.next()
            await message.reply(
                "Очень жаль, что вы не сможете приехать!\n"
                "Напишите, пожалуйста, причину, по которой вы не сможете приехать.",
                reply_markup=yes_no.kbd_remove
            )


async def process_reason(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['reason'] = message.text

    await message.reply(
        "Благодарим за разъяснение! Всего доброго!"
    )

    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_confirmation_poll, lambda msg: msg.text == 'Подтвердить госпитализацию')
    dp.register_message_handler(process_confirmation, state=PollForm.is_confirmed)
    dp.register_message_handler(process_reason, state=PollForm.reason)
