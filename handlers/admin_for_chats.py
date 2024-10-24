from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from utils.admin_router_for_chats import admin_router_for_chats
from loader import bot_base, settings_dict
from handlers.gratitude_checker import check_new_status, get_username
from utils.message_cleaner import message_cleaner


@admin_router_for_chats.message(Command('add_points'))
async def add_points_for_user_in_chat(msg: Message, command: CommandObject):
    """Добавление репутации администратором через общий чат"""
    if msg.reply_to_message:
        try:
            user_id = msg.reply_to_message.from_user.id
            await bot_base.add_points(user_id, int(command.args) if command.args else 1)
            user_name = await get_username(msg.chat.id, msg.reply_to_message.from_user.id)
            user_status = await check_new_status(user_id)
            user = await bot_base.get_user_info(msg.reply_to_message.from_user.id)
            msg_text = f"""{settings_dict["admin_add"].format(
                        user_name=user_name,
                        user_rep=user[1],
                        user_points=user[2],
                        user_status=user_status if user_status != "None" else "Отсутствует",
                        add_points=int(command.args) if command.args else 1,
                        reduce_points=0
                    )}"""
            mess = await msg.reply(msg_text)
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
        except ValueError:
            mess = await msg.reply('Аргументом команды должно быть целое число\!')
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@admin_router_for_chats.message(Command('reduce_points'))
async def reduce_from_the_user(msg: Message, command: CommandObject):
    """Списывание баллов администратором через общий чат"""
    from handlers.admin_panel import escape_special_chars
    if msg.reply_to_message:
        try:
            user_id = msg.reply_to_message.from_user.id
            await bot_base.reduce_user_balance(user_id, int(command.args) if command.args else 1)
            user = await bot_base.get_user_info(user_id)
            user_name = await get_username(msg.chat.id, user_id)
            msg_text = settings_dict["admin_reduce"].format(
                        user_name=escape_special_chars(user_name),
                        user_rep=user[1],
                        user_points=user[2],
                        user_status=user[3] if user[3] != "None" else "Отсутствует",
                        add_points=0,
                        reduce_points=int(command.args) if command.args else 1
                    )
            mess = await msg.reply(msg_text)
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
        except ValueError:
            mess = await msg.reply('Аргументом команды должно быть целое число\!')
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@admin_router_for_chats.message(Command('help'))
async def help_for_admin(msg: Message):
    """Подсказка для администратора"""
    from handlers.admin_panel import escape_special_chars
    msg_text = escape_special_chars('Подсказка для администратора:'
                                    '\n\n/add_points - в ответ на сообщение пользователя добавляет репутацию. Без указания очков добавляет '
                                    '1 репутацию, с указанием добавляет указанное кол-во репутации. '
                                    '\nНапример "/add_points 5" добавит 5 репутации\n\n'
                                    '/reduce_points - в ответ на сообщение пользователя списывает баллы. Без указания очков списывает '
                                    '1 балл, с указанием списывает указанное кол-во баллов.'
                                    '\nНапример "/reduce_points 5" спишет 5 баллов\n\n'
                                    'Переменные для уведомлений:\n'
                                    '{user_name} - @username рользователя (шаблонное значение @UserName)\n'
                                    '{user_rep} - отображает всю репутацию пользователя (шаблонное значение 10)\n'
                                    '{user_points} - показывает сколько баллов на счету у пользователя (шаблонное значение 5)\n'
                                    '{user_status} - статус пользователя (шаблонное значение "Царь всея чата")\n'
                                    '{add_points} - количество добавляемых очков администратором (использовать для уведомления "Начисление от администратора") (шаблонное значение 2)\n'
                                    '{reduce_points} - количество списываемых администратором быллов (использовать для уведомления "Списание баллов") (шаблонное значение 3)\n')
    mess = await msg.answer(msg_text)
    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
