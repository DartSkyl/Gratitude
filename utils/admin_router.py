from config import ADMIN_ID
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsAdminFilter(BaseFilter):
    """Фильтр, проверяющий является ли отправитель сообщения админом"""
    def __init__(self, admin_id):

        # Список ID администраторов прописывается вручную
        self.admins_id = admin_id

    async def __call__(self, message: Message) -> bool:
        from loader import settings_dict
        return message.from_user.id in self.admins_id and message.chat.id not in settings_dict['chats']


admin_router = Router()

# Выше описанный фильтр добавляем прямо в роутер
admin_router.message.filter(IsAdminFilter(ADMIN_ID))
