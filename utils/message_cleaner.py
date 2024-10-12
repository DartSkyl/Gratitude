from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from loader import bot

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)


async def remove_message(chat_id: int, msg_id: int, job_id: str):
    """Удаляет сообщение из чата"""
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    await message_cleaner.remove_job(job_id)


class MessageCleaner:
    """Планировщик, который будет удалять все сообщения от бота через заданное время"""
    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._interval = 1

    async def start_cleaner(self):
        """Запуск чистильщика"""
        self._scheduler.start()

    async def schedule_message_deletion(self, chat_id: int, msg_id: int):
        """Запланировать удаление сообщения"""
        job_id = (str(msg_id) + str(chat_id))
        self._scheduler.add_job(func=remove_message,
                                kwargs={'chat_id': chat_id, 'msg_id': msg_id, 'job_id': job_id},
                                trigger='interval',
                                minutes=self._interval,
                                id=job_id,
                                max_instances=1)

    async def remove_job(self, job_id):
        self._scheduler.remove_job(job_id)


message_cleaner = MessageCleaner()
