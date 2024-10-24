import asyncio
import datetime
from aiogram.types import BotCommand
import handlers  # noqa
from loader import bot_base, load_from_db, dp, bot, settings_dict, app_run
from utils.message_cleaner import message_cleaner


async def start_up():
    await bot_base.check_db_structure()
    await load_from_db()
    await message_cleaner.set_interval(settings_dict['interval'])
    await message_cleaner.start_cleaner()
    await bot.set_my_commands([
        BotCommand(command='karma', description='Отображает статистику пользователя'),
        BotCommand(command='rating', description='Топ 10 чата'),
        BotCommand(command='help', description='Подсказка')
    ])
    # await app_run()
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    print('Стартуем')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
