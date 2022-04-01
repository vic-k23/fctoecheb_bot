import logging
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.utils import exceptions

from keybords import yes_no


class PollForm(StatesGroup):
    """
    Object for poll results
    """
    is_confirmed = State()  # Подтверждение госпитализации
    reason = State()  # Причина, по которой пациент не сможет приехать, если такое случится


async def start_confirmation_poll(message: Message):
    """
    This handler will be called when user sends `Подтвердить госпитализацию` command.
    """
    try:
        # Set state
        await PollForm.is_confirmed.set()
        await message.reply("Подтверждаете ли вы своё прибыте на госпитализацию к сроку?", reply_markup=yes_no.kbd)
    except Exception as ex:
        logging.exception(ex)


async def process_confirmation(message: Message, state: FSMContext):
    """
    Process conformation of hospitalization
    """
    async with state.proxy() as data:
        data['confirmation'] = message.text
    if message.text == "Да":
        await message.reply(
            "Благодарим за подтверждение!",
            reply_markup=yes_no.kbd_remove
        )
        # Save results and then close state
        await state.finish()
    else:
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
