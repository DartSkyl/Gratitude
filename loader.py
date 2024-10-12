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
dp.include_router(admin_router)
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
    'gratitude_list': {'спасибо', 'благодарю'}
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
        if elem[0] == 'achievement':
            settings_dict[elem[0]] = int(elem[1])
        else:
            settings_dict[elem[0]] = elem[1]

    for elem in await bot_base.get_gratitude_list():
        settings_dict['gratitude_list'].add(elem[0])


# async def start_up():
#     await bot_base.check_db_structure()
#     await load_from_db()
#     with open('bot.log', 'a') as log_file:
#         log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
#     print('Стартуем')
#     await dp.start_polling(bot)
