import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from utils.admin_router import admin_router
from database import BotBase


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
bot_base = BotBase()


async def start_up():
    await bot_base.check_db_structure()
    dp.include_router(admin_router)
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    print('Стартуем')
    await dp.start_polling(bot)
