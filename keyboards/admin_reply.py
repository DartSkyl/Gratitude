from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup


main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='📋 Управление балансом')], [KeyboardButton(text='⚙️ Настройки')]
], resize_keyboard=True)

cancel_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='🚫 Отмена')]], resize_keyboard=True)
