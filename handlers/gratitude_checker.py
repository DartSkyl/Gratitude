import time

from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types.chat_member_member import ChatMemberMember

from loader import bot_base, checker_router, status_dict, settings_dict, bot
from utils.message_cleaner import message_cleaner


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
        if c > 0 and user_to_status != status_dict[c]:  # Значит получен новый статус
            await bot_base.set_user_status(user_id, status_dict[c])
            return status_dict[c], ach
    return None, ach


async def get_username(chat_id, user_id):
    a = await bot.get_chat_member(chat_id, user_id)
    if isinstance(a, ChatMemberMember):
        return ('@' + a.user.username) if a.user.username else a.user.first_name
    return None


# Ключ - id пользователя, значение - время последней благодарности в секундах (unix)
anti_spam_dict = {}


@checker_router.message(Command('karma'))
async def view_user_points_and_status(msg: Message):
    """Выводим показания очков и статуса"""
    if not msg.reply_to_message:
        user = await bot_base.get_user_info(msg.from_user.id)
        msg_text = (f'Ваша репутация: <b>{user[1]}</b>\n'
                    f'Статус: <i>{user[3] if user[3] != "None" else "Отсутствует"}</i>\n'
                    f'На счету: <b>{user[2]}</b> баллов')
        mess = await msg.reply(msg_text)
        await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
    else:
        user = await bot_base.get_user_info(msg.reply_to_message.from_user.id)
        user_name = await get_username(msg.chat.id, msg.reply_to_message.from_user.id)
        msg_text = (f'Статистика {user_name}\nРепутация: <b>{user[1]}</b>\n'
                    f'Статус: <i>{user[3] if user[3] != "None" else "Отсутствует"}</i>\n'
                    f'На счету: <b>{user[2]}</b> баллов')
        mess = await msg.answer(msg_text)
        await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@checker_router.message(Command('rating'))
async def get_rating(msg: Message):
    """Выдает рейтинг пользователей"""
    all_users = await bot_base.get_all_users()
    msg_text = f'Рейтинг чата:\n\n'
    for u in all_users:
        user_name = await get_username(msg.chat.id, u[0])
        if user_name:
            msg_text += f'{user_name} - {u[1]} репутации, статус <i>{u[3] if u[3] != "None" else "Отсутствует"}</i>\n'
    mess = await msg.answer(msg_text)
    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@checker_router.message(Command('help'))
async def help_for_users(msg: Message):
    """Подсказка для пользователей"""
    msg_text = ('Подсказка для пользователя:\n\n'
                '/karma - отображает текущую статистику пользователя, вызвавшего команду. '
                'В ответ на сообщение другого пользователя отображает статистику того '
                'пользователя, в ответ на чье сообщение была вызвана команда')
    mess = await msg.answer(msg_text)
    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)


@checker_router.message()
async def check_gratitude_in_message(msg: Message):
    """Основная функция, которая будет проверять есть ли благодарность в сообщении"""
    if msg.reply_to_message:

        # Антиспам проверяет, что бы с последней благодарности было не больше 60 секунд
        last = anti_spam_dict.get(msg.reply_to_message.from_user.id, 0)
        last = int(time.time()) - last
        if last >= 60:
            user_id = msg.from_user.id  # Кто благодарит
            user_to_id = msg.reply_to_message.from_user.id  # Кого благодарит
            if any(word in msg.text.lower() for word in settings_dict['gratitude_list']) and user_id != user_to_id:
                await bot_base.add_points(user_to_id, 1)
                anti_spam_dict[user_to_id] = int(time.time())
                # Возвращается кортеж (статус, достижение)
                user_status = await check_new_status(user_to_id)
                msg_text = (f'<b><i>{msg.reply_to_message.from_user.first_name}</i>, '
                            f'Репутация + 1!</b>'
                            f'\n{settings_dict["new_gratitude"]}\n' +
                            (f"{settings_dict['new_status']}\n" if user_status[0] else '') +
                            (settings_dict['new_achievement'] if user_status[1] else '' + '\nРейтинг чата /rating'))
                mess = await msg.reply(msg_text)
                await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
        else:
            msg_text = f'Следующую благодарность можно будет получить через <b><i>{60 - last}</i></b> сек.'
            mess = await msg.reply(msg_text)
            await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
