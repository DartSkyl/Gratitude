import asyncio
import datetime
import handlers  # noqa
from loader import bot_base, load_from_db, dp, bot
from utils.message_cleaner import message_cleaner


async def start_up():
    await bot_base.check_db_structure()
    await load_from_db()
    await message_cleaner.start_cleaner()
    with open('bot.log', 'a') as log_file:
        log_file.write(f'\n========== New bot session {datetime.datetime.now()} ==========\n\n')
    print('Стартуем')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(start_up())
    except KeyboardInterrupt:
        print('Хорош, бро')
