from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from utils.admin_router import admin_router
from utils.admin_router_for_chats import admin_router_for_chats
from utils.checker_router import checker_router
from database import BotBase
from pyrogram import Client

api_id = 22761163
api_hash = "8b23c6b5877145fc046a0752a7cd20ac"
py_bot = '7901150176:AAES5lZ_6U-iEZ-iC2D0-91MP78DlvkFLAo'

app = Client("gratitude_checker",
             # api_id=api_id,
             # api_hash=api_hash,
             # bot_token=py_bot
             )


async def app_run():
    await app.start()


bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
    parse_mode=ParseMode.MARKDOWN_V2
))
dp = Dispatcher(bot=bot, storage=MemoryStorage())
dp.include_router(admin_router)
dp.include_router(admin_router_for_chats)
dp.include_router(checker_router)
bot_base = BotBase()
status_dict = dict()  # Ключ - необходимое кол-во очков для его достижения, значение - название статуса
settings_dict = {  # Содержит в себе настройки уведомлений и порога достижений
    'achievement': 5,
    'new_gratitude': 'Вы повысили репутацию {user_name} на 1 и теперь она {user_points}\. {user_name}\, '
                     'спасибо\, что помогаете нашему сообществу 🌹',
    'new_achievement': 'Вы получили новое достижение',
    'new_status': 'Вы достигли нового статуса {user_status}',
    'admin_add': 'Администрация благодарит Вас за активное участие\nРепутация \+ {add_points}',
    'admin_reduce': '{user_name}, С вашего баланса были списаны баллы в размере {reduce_points}',
    'karma': 'Статистика {user_name}\n⭐️ Репутация: {user_rep}\n'
             '🎖 Статус: {user_status}\n'
             '🏵 На счету: {user_points} баллов',
    'rating': '{user_name} \- {user_rep} репутации, статус {user_status}\n',
    'admin_rep_reduce': '{user_name}, С вашего баланса были списана репутация в размере {reduce_points}',
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
