from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import bot_base, checker_router, status_dict


gratitude_list = ['спасибо', 'благодарю']


@checker_router.message(Command('karma'))
async def view_user_points_and_status(msg: Message):
    """Выводим показания очков и статуса"""



@checker_router.message()
async def check_gratitude_in_message(msg: Message):
    """Основная функция, которая будет проверять есть ли благодарность в сообщении"""
    if msg.reply_to_message:
        user_id = msg.from_user.id  # Кто благодарит
        user_to_id = msg.reply_to_message.from_user.id  # Кого благодарит
        if any(word in msg.text.lower() for word in gratitude_list) and user_id != user_to_id:
            await bot_base.add_points(msg.reply_to_message.from_user.id, 1)
            await msg.reply(f'Засчитан для {msg.reply_to_message.from_user.first_name}!')
