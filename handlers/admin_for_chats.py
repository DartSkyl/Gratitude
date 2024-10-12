from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from utils.admin_router_for_chats import admin_router_for_chats
from loader import bot_base, settings_dict
from handlers.gratitude_checker import check_new_status
from utils.message_cleaner import message_cleaner


@admin_router_for_chats.message(Command('add_points'))
async def add_points_for_user_in_chat(msg: Message, command: CommandObject):
    """Добавление репутации администратором через общий чат"""
    if msg.reply_to_message:
        try:
            user_id = msg.reply_to_message.from_user.id
            await bot_base.add_points(user_id, int(command.args) if command.args else 1)
            user_status = await check_new_status(user_id)
            msg_text = (f'<b><i>{msg.reply_to_message.from_user.first_name}</i>, '
                        f'Репутация + {command.args if command.args else 1}!</b>'
                        f'\n{settings_dict["admin_add"]}\n' +
                        (f"{settings_dict['new_status']}\n" if user_status[0] else '') +
                        (settings_dict['new_achievement'] if user_status[1] else '' + '\nРейтинг чата /rating'))
            mess = await msg.reply(msg_text)
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
        except ValueError:
            mess = await msg.reply('Аргументом команды должно быть целое число!')
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@admin_router_for_chats.message(Command('reduce_points'))
async def reduce_from_the_user(msg: Message, command: CommandObject):
    """Списывание баллов администратором через общий чат"""
    if msg.reply_to_message:
        try:
            user_id = msg.reply_to_message.from_user.id
            await bot_base.reduce_user_balance(user_id, int(command.args) if command.args else 1)
            msg_text = (f'<b><i>{msg.reply_to_message.from_user.first_name}</i>, '
                        f'Баллы - {command.args if command.args else 1}!</b>'
                        f'\n{settings_dict["admin_reduce"]}\n\nРейтинг чата /rating')
            mess = await msg.reply(msg_text)
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
        except ValueError:
            mess = await msg.reply('Аргументом команды должно быть целое число!')
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@admin_router_for_chats.message(Command('help'))
async def help_for_admin(msg: Message):
    """Подсказка для администратора"""
    msg_text = ('Подсказка для администратора:'
                '\n\n/add_points - в ответ на сообщение пользователя добавляет репутацию. Без указания очков добавляет '
                '1 репутацию, с указанием добавляет указанное кол-во репутации. '
                '\nНапример "/add_points 5" добавит 5 репутации\n\n'
                '/reduce_points - в ответ на сообщение пользователя списывает баллы. Без указания очков списывает '
                '1 балл, с указанием списывает указанное кол-во баллов.'
                '\nНапример "/reduce_points 5" спишет 5 баллов')
    mess = await msg.answer(msg_text)
    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


