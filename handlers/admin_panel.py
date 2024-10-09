from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.admin_router import admin_router


@admin_router.message(Command('start'))
async def start_function(msg: Message):
    """Функция запуска бота"""
    await msg.answer('Пидр!')
