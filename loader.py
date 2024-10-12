import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from utils.admin_router import admin_router
from utils.admin_router_for_chats import admin_router_for_chats
from utils.checker_router import checker_router
from database import BotBase


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
dp.include_router(admin_router)
dp.include_router(admin_router_for_chats)
dp.include_router(checker_router)
bot_base = BotBase()
status_dict = dict()  # Ключ - необходимое кол-во очков для его достижения, значение - название статуса
settings_dict = {  # Содержит в себе настройки уведомлений и порога достижений
    'achievement': 5,
    'new_gratitude': 'Вас поблагодарили!\nВаша репутация возросла!',
    'new_achievement': 'Вы получили новое достижение',
    'new_status': 'Вы достигли нового статуса!',
    'admin_add': 'Администрация благодарит Вас за активное участие!',
    'admin_reduce': 'С вашего баланса были списаны очки!',
    'gratitude_list': {'спасибо', 'благодарю'},
    'interval': 3,
    'chats': set()
}


async def load_from_db():
    """Выгружаем из базы статусы и настройки"""
    for elem in await bot_base.get_all_status():
        status_dict[elem[1]] = elem[0]
    if len(status_dict) == 0:  # Если в базе пусто, то установим статусы "по умолчанию"
        status_dict[10] = 'Любитель чата'
        status_dict[15] = 'Знаток чата'
        status_dict[20] = 'Эксперт чата'

    for elem in await bot_base.get_all_settings():
        if elem[0] in ['achievement', 'interval']:
            settings_dict[elem[0]] = int(elem[1])
        else:
            settings_dict[elem[0]] = elem[1]

    for elem in await bot_base.get_gratitude_list():
        settings_dict['gratitude_list'].add(elem[0])

    for elem in await bot_base.get_chats():
        settings_dict['chats'].add(elem[0])
