from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import dp, bot_base


gratitude_list = ['спасибо', 'благодарю']


@dp.message()
async def check_gratitude_in_message(msg: Message):
    """Основная функция, которая будет проверять есть ли благодарность в сообщении"""
    if msg.reply_to_message:
        if any(word in msg.text.lower() for word in gratitude_list):
            await bot_base.add_points(msg.reply_to_message.from_user.id, 1)
