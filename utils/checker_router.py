from aiogram import Router
from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        from loader import settings_dict
        return message.chat.id in settings_dict['chats']


checker_router = Router()
checker_router.message.filter(IsChatFilter())
