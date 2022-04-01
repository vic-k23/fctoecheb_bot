import settings
import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import welcome_handlers, conformation_poll_handlers

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=settings.API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


if __name__ == '__main__':
    welcome_handlers.register_handlers(dp)
    conformation_poll_handlers.register_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
