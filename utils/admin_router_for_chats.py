from config import ADMIN_ID
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsAdminFilter(BaseFilter):
    """Фильтр, проверяющий является ли отправитель сообщения админом"""
    def __init__(self, admin_id: int):

        # Список ID администраторов прописывается вручную
        self.admins_id = admin_id

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admins_id


admin_router_for_chats = Router()

# Выше описанный фильтр добавляем прямо в роутер
admin_router_for_chats.message.filter(IsAdminFilter(ADMIN_ID))
