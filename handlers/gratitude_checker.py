import time

from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types.chat_member_member import ChatMemberMember
from aiogram.types.chat_member_left import ChatMemberLeft
from aiogram.types import ChatMember
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, ADMINISTRATOR, MEMBER

from loader import bot_base, checker_router, status_dict, settings_dict, bot, dp
from utils.message_cleaner import message_cleaner
from config import ADMIN_ID


async def check_new_status(user_id):
    """Функция проверяет, получил ли пользователь новый статус или достижение"""
    # Берем из базы сразу все необходимые данные для проверки достиг ли пользователь нового статуса и порога достижений
    user_to_points, user_to_status, user_to_last_achievement = await bot_base.get_user_points_status_achievements(user_id)
    # Ниже проверяем, достиг ли пользователь порога достижений
    ach = user_to_points - (user_to_last_achievement if user_to_last_achievement else 0)
    if ach >= settings_dict['achievement']:
        await bot_base.set_last_achievement(user_id, user_to_points)
        ach = True
    else:
        ach = False
    status_points_list = sorted(status_dict)
    c = 0  # Нужно для перебора "статусных" очков
    for i in range(len(status_points_list)):
        if user_to_points >= status_points_list[i]:
            c = status_points_list[i]
        else:
            if c > 0 and user_to_status != status_dict[c]:  # Значит получен новый статус
                await bot_base.set_user_status(user_id, status_dict[c])
                return status_dict[c], ach
    else:
        try:  # Просто психанул
            if c > 0 and user_to_status != status_dict[c]:  # Значит получен новый статус
                await bot_base.set_user_status(user_id, status_dict[c])
                return status_dict[c], ach
            elif user_to_status != status_dict[c]:
                await bot_base.set_user_status(user_id, 'None')
        except KeyError:
            await bot_base.set_user_status(user_id, 'None')
    return None, ach


async def get_username(chat_id, user_id):
    a = await bot.get_chat_member(chat_id, user_id)
    print(type(a))
    if not isinstance(a, ChatMemberLeft):
        print(a.user.username)
        return ('@' + a.user.username) if a.user.username else a.user.first_name
    # print(type(a))
    return None


# Ключ - id пользователя, значение - время последней благодарности в секундах (unix)
anti_spam_dict = {}


@checker_router.message(Command('karma'))
async def view_user_points_and_status(msg: Message):
    """Выводим показания очков и статуса"""
    try:
        from handlers.admin_panel import escape_special_chars
        if not msg.reply_to_message:
            try:
                user = await bot_base.get_user_info(msg.from_user.id)
                user_name = await get_username(msg.chat.id, msg.from_user.id)
                msg_text = settings_dict['karma'].format(
                    user_name=escape_special_chars(user_name),
                    user_rep=user[1],
                    user_points=user[2],
                    user_status=user[3] if user[3] != "None" else "Отсутствует",
                    add_points=0,
                    reduce_points=0
                )
                print(user[3] if user[3] else "Отсутствует")
            except IndexError:
                user_name = await get_username(msg.chat.id, msg.from_user.id)
                msg_text = settings_dict['karma'].format(
                    user_name=escape_special_chars(user_name),
                    user_rep=0,
                    user_points=0,
                    user_status="Отсутствует",
                    add_points=0,
                    reduce_points=0
                )
            mess = await msg.reply(msg_text)
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
        else:
            user_name = await get_username(msg.chat.id, msg.reply_to_message.from_user.id)
            try:
                user = await bot_base.get_user_info(msg.reply_to_message.from_user.id)
                msg_text = settings_dict['karma'].format(
                    user_name=escape_special_chars(user_name),
                    user_rep=user[1],
                    user_points=user[2],
                    user_status=user[3] if user[3] != "None" else "Отсутствует",
                    add_points=0,
                    reduce_points=0
                )
            except IndexError:
                msg_text = settings_dict['karma'].format(
                    user_name=escape_special_chars(user_name),
                    user_rep=0,
                    user_points=0,
                    user_status="Отсутствует",
                    add_points=0,
                    reduce_points=0
                )
            mess = await msg.answer(msg_text)
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
    except Exception as e:
        print(e, '\nKarma, user_name=None')


@checker_router.message(Command('rating'))
async def get_rating(msg: Message):
    """Выдает рейтинг пользователей"""
    from handlers.admin_panel import escape_special_chars
    all_users = await bot_base.get_all_users()
    msg_text = f'Рейтинг чата:\n\n'
    for u in all_users:
        user_name = await get_username(msg.chat.id, u[0])
        if user_name:
            msg_text += settings_dict['rating'].format(
                user_name=escape_special_chars(user_name),
                user_rep=u[1],
                user_points=u[2],
                user_status=u[3] if u[3] else "Отсутствует",
                add_points=0,
                reduce_points=0
            )
            msg_text += '\n'
    mess = await msg.answer(msg_text)
    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@checker_router.message(Command('help'))
async def help_for_users(msg: Message):
    """Подсказка для пользователей"""
    from handlers.admin_panel import escape_special_chars
    msg_text = escape_special_chars('Подсказка для пользователя:\n\n'
                '/karma - отображает текущую статистику пользователя, вызвавшего команду. '
                'В ответ на сообщение другого пользователя отображает статистику того '
                'пользователя, в ответ на чье сообщение была вызвана команда\n\n'
                '/rating - отображает список участников, кто получил хотя бы одну благодарность')
    mess = await msg.answer(msg_text)
    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@checker_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER << MEMBER))
async def member_left_chat(chat_member: ChatMember):
    """Удаляем из базы тех кто отписался"""
    try:
        if chat_member.from_user.id not in ADMIN_ID:
            await bot_base.drop_user(chat_member.from_user.id)
        else:
            await bot_base.drop_user(chat_member.old_chat_member.user.id)
    except Exception as e:
        print(e, '\nChatMemberLeft error')


@checker_router.message()
async def check_gratitude_in_message(msg: Message):
    """Основная функция, которая будет проверять есть ли благодарность в сообщении"""
    try:
        if msg.reply_to_message:
            user_id = msg.from_user.id  # Кто благодарит
            user_to_id = msg.reply_to_message.from_user.id  # Кого благодарит
            if any(word in msg.text.lower() for word in settings_dict['gratitude_list']) and user_id != user_to_id:
                from handlers.admin_panel import escape_special_chars
                if user_id not in ADMIN_ID:
                    # Антиспам проверяет, что бы с последней благодарности было не больше 60 секунд
                    last = anti_spam_dict.get(msg.reply_to_message.from_user.id, 0)
                    last = int(time.time()) - last
                    if last >= 60:

                        user_name = await get_username(msg.chat.id, user_to_id)
                        await bot_base.add_points(user_to_id, 1)
                        # user_points = await bot_base.get_user_points(user_to_id)
                        user = await bot_base.get_user_info(user_to_id)
                        user_rep = user[1]
                        user_points = user[2]
                        anti_spam_dict[user_to_id] = int(time.time())
                        # Возвращается кортеж (статус, достижение)
                        user_status = await check_new_status(user_to_id)
                        msg_text = (f'{settings_dict["new_gratitude"]}' +
                                    (f"{settings_dict['new_status']}\n" if user_status[0] else '') +
                                    (settings_dict['new_achievement'] if user_status[1]
                                     else '')).format(
                            user_name=escape_special_chars(user_name),
                            user_rep=user_rep,
                            user_points=user_points,
                            user_status=user_status[0],
                            add_points=0,
                            reduce_points=0
                        )
                        mess = await msg.reply(msg_text)
                        await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
                    else:
                        msg_text = f'Следующую благодарность можно будет получить через {60 - last} сек\.'
                        mess = await msg.reply(msg_text)
                        await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
                else:
                    if any(word in msg.text.lower() for word in settings_dict['gratitude_list']):
                        if 'спасибо за помощь' in msg.text.lower():
                            add_points = 2
                        else:
                            add_points = 1
                        user_name = await get_username(msg.chat.id, user_to_id)
                        await bot_base.add_points(user_to_id, add_points)
                        user = await bot_base.get_user_info(user_to_id)
                        user_rep = user[1]
                        user_points = user[2]
                        user_status = await check_new_status(user_to_id)
                        msg_text = (f'{settings_dict["admin_add"]}' +
                                    (f"{settings_dict['new_status']}\n" if user_status[0] else '') +
                                    (settings_dict['new_achievement'] if user_status[1]
                                     else '')).format(
                            user_name=escape_special_chars(user_name),
                            user_rep=user_rep,
                            user_points=user_points,
                            user_status=user_status[0],
                            add_points=add_points,
                            reduce_points=0
                        )
                        mess = await msg.reply(msg_text)
                        await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
    except Exception as e:
        print(e, '\nCatch gratitude')
