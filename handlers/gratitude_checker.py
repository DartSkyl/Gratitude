from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from loader import bot_base, checker_router, status_dict, settings_dict


# gratitude_list = ['спасибо', 'благодарю']


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


@checker_router.message(Command('karma'))
async def view_user_points_and_status(msg: Message):
    """Выводим показания очков и статуса"""
    pass


@checker_router.message()
async def check_gratitude_in_message(msg: Message):
    """Основная функция, которая будет проверять есть ли благодарность в сообщении"""
    if msg.reply_to_message:
        user_id = msg.from_user.id  # Кто благодарит
        user_to_id = msg.reply_to_message.from_user.id  # Кого благодарит
        if any(word in msg.text.lower() for word in settings_dict['gratitude_list']) and user_id != user_to_id:
            await bot_base.add_points(user_to_id, 1)
            # Возвращается кортеж (статус, достижение)
            user_status = await check_new_status(user_to_id)
            msg_text = (f'<b>{msg.reply_to_message.from_user.first_name}!</b>\n{settings_dict["new_gratitude"]}\n' +
                        (f"{settings_dict['new_status']}\n" if user_status[0] else '') +
                        (settings_dict['new_achievement'] if user_status[1] else ''))
            await msg.reply(msg_text)
