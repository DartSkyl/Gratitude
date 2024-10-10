import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from utils.admin_router import admin_router
from utils.checker_router import checker_router
from database import BotBase


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
bot_base = BotBase()
status_dict = dict()  # Ключ - необходимое кол-во очков для его достижения, значение - название статуса


async def load_from_db():
    """Выгружаем из базы статусы"""
    for elem in await bot_base.get_all_status():
        status_dict[elem[1]] = elem[0]
    if len(status_dict) == 0:  # Если в базе пусто, то установим статус "по умолчанию"
        status_dict[10] = 'Первооткрыватель'


async def start_up():
    await bot_base.check_db_structure()
    await load_from_db()
    dp.include_router(admin_router)
    dp.include_router(checker_router)
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    print('Стартуем')
    await dp.start_polling(bot)
