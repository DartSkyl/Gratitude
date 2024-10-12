from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.admin_router import admin_router
from keyboards.admin_reply import *
from keyboards.admin_inline import *
from states import AdminStates
from loader import status_dict, bot_base, settings_dict, bot
from handlers.gratitude_checker import check_new_status, get_username
from config import CHAT_ID
from utils.message_cleaner import message_cleaner


@admin_router.message(Command('start'))
async def start_function(msg: Message, state: FSMContext):
    """Функция запуска админпанели"""
    await state.clear()
    await msg.answer(f'Добрый день <b>{msg.from_user.first_name}</b>😀\nВыберете действие:', reply_markup=main_menu)


@admin_router.message(F.text == '🚫 Отмена')
async def cancel_func(msg: Message, state: FSMContext):
    """Все отменяем и сбрасываем"""
    await state.clear()
    await msg.answer(f'Действие отменено\nВыберете действие:', reply_markup=main_menu)


@admin_router.message(F.text == '⚙️ Настройки')
async def get_settings_menu(msg: Message):
    """Выводит меню настроек"""
    await msg.answer('Выберете настройку:', reply_markup=all_settings)


@admin_router.callback_query(F.data.startswith('set_'))
async def choice_setting(callback: CallbackQuery):
    """Выбор настройки и запуск ее изменений"""
    await callback.answer()
    setting_dict = {
        'set_status': ('Выберете действие:', status_setting),
        'set_level': (f'Порог достижения на данный момент <b>{settings_dict["achievement"]}</b> репутации', level_setting),
        # 'set_notification': ('Выберете уведомление для изменения:', notification_setting),
        # 'set_gratitude': ('Выберете действие:', gratitude_list_setting)
    }
    await callback.message.answer(setting_dict[callback.data][0], reply_markup=setting_dict[callback.data][1])


# --------------------
# Управление статусами
# --------------------


@admin_router.callback_query(F.data.startswith('status_'))
async def status_management(callback: CallbackQuery, state: FSMContext):
    """Управление статусами"""
    await callback.answer()
    if callback.data == 'status_view':
        msg_text = 'Установленные статусы:\n\n'
        for points_need, status_name in status_dict.items():
            msg_text += f'<b>{status_name}</b>: <i>{points_need}</i> очков\n'
        await callback.message.answer(msg_text, reply_markup=await view_status_list(status_dict))
        pass
    else:
        await state.set_state(AdminStates.status_add_name)
        await callback.message.answer('Введите название статуса:', reply_markup=cancel_button)


@admin_router.message(AdminStates.status_add_name)
async def get_status_name(msg: Message, state: FSMContext):
    """Ловим название статуса"""
    await state.set_data({'status_name': msg.text})
    await state.set_state(AdminStates.status_add_points)
    await msg.answer('Введите число очков для достижения статуса:')


@admin_router.message(AdminStates.status_add_points)
async def get_status_points(msg: Message, state: FSMContext):
    """Ловим очки статуса"""
    try:
        status_name = (await state.get_data())['status_name']
        for points, status in status_dict.items():
            if status == status_name:
                status_dict.pop(points)
                status_dict[int(msg.text)] = status_name
                break
        else:
            status_dict[int(msg.text)] = status_name
        await bot_base.add_status(status_name, int(msg.text))
        await msg.answer('Новый статус добавлен!', reply_markup=main_menu)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка! Введите целое число:')


@admin_router.callback_query(F.data.startswith('del_'))
async def remove_status(callback: CallbackQuery):
    """Удаляем статус"""
    rm_status = status_dict.pop(int(callback.data.replace('del_', '')))
    await bot_base.remove_status(rm_status)
    msg_text = 'Установленные статусы:\n\n'
    for points_need, status_name in status_dict.items():
        msg_text += f'<b>{status_name}</b>: <i>{points_need}</i> очков\n'
    await callback.message.edit_text(msg_text, reply_markup=await view_status_list(status_dict))


# --------------------
# Управление очками
# --------------------


@admin_router.message(F.text == '📋 Управление балансом')
async def balance_management_menu(msg: Message, state: FSMContext):
    """Открываем меню управления балансом пользователей"""
    await msg.answer('Перешлите сообщение от пользователя, над чьим балансом хотите провести манипуляцию:')
    await state.set_state(AdminStates.select_user)


@admin_router.message(AdminStates.select_user, F.forward_from.as_('reply'))
async def select_user_for_manipulation(msg: Message, state: FSMContext, reply=None):
    """Запоминаем выбранного юзера"""
    if reply:
        try:
            user_info = await bot_base.get_user_info(reply.id)
            msg_text = (f'Пользователь <b>{reply.first_name}</b>:\n'
                        f'Всего репутации получено: <b>{user_info[1]}</b>\n'
                        f'На балансе: <b>{user_info[2]}\n</b>'
                        f'Статус пользователя: <b>{user_info[3]}</b>')
        except IndexError:
            # Значит пользователя нет в базе
            msg_text = (f'Пользователь <b>{reply.first_name}</b>:\n'
                        f'Всего репутации получено: <b>0</b>\n'
                        f'На балансе: <b>0\n</b>'
                        f'Статус пользователя: <b>None</b>')

        await state.set_data({'uid': reply.id, 'ufn': reply.first_name})
        await msg.answer(msg_text, reply_markup=balance_menu)


@admin_router.callback_query(AdminStates.select_user, F.data.startswith('balance_'))
async def user_balance_manipulation(callback: CallbackQuery, state: FSMContext):
    """Здесь начинается процесс изменения баланса пользователя"""
    await callback.answer()
    action_dict = {
        'balance_add': (AdminStates.balance_add, 'Введите количество репутации которое хотите добавить:'),
        'balance_reduce': (AdminStates.balance_reduce, 'Введите количество очков для списания:')
    }
    await callback.message.answer(action_dict[callback.data][1], reply_markup=cancel_button)
    await state.set_state(action_dict[callback.data][0])


@admin_router.message(AdminStates.balance_add)
async def user_balance_add(msg: Message, state: FSMContext):
    """Добавление баланса пользователю"""
    try:
        user = await state.get_data()
        await bot_base.add_points(user['uid'], int(msg.text))
        await msg.answer(f'Пользователю <b>{user["ufn"]}</b> начислено {msg.text} репутации', reply_markup=main_menu)
        await check_new_status(user['uid'])

        for chat in CHAT_ID:  # Ищем юзера по всем чатам и по этим же чатам и отправляем уведомление
            try:
                user_name = await get_username(chat, user['uid'])
                if user_name:
                    msg_text = f'{user_name}, Вам начислено {msg.text} репутации\n{settings_dict["admin_add"]}'
                    mess = await bot.send_message(chat_id=chat, text=msg_text)
                    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
            except Exception as e:
                print(e)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка! Введите целое число:')


@admin_router.message(AdminStates.balance_reduce)
async def user_balance_reduce(msg: Message, state: FSMContext):
    """Списание балов с баланса пользователя"""
    try:
        user = await state.get_data()
        await bot_base.reduce_user_balance(user['uid'], int(msg.text))
        await msg.answer(f'У пользователя <b>{user["ufn"]}</b> списано {msg.text} очков', reply_markup=main_menu)
        for chat in CHAT_ID:  # Ищем юзера по всем чатам и по этим же чатам и отправляем уведомление
            try:
                user_name = await get_username(chat, user['uid'])
                if user_name:
                    msg_text = f'{user_name}, у Вас списано {msg.text} балов\n{settings_dict["admin_reduce"]}'
                    mess = await bot.send_message(chat_id=chat, text=msg_text)
                    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
            except Exception as e:
                print(e)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка! Введите целое число:')


# --------------------
# Установка порога достижения
# --------------------


@admin_router.callback_query(F.data == 'level_set')
async def change_achievement(callback: CallbackQuery, state: FSMContext):
    """Запускаем изменения порога достижений"""
    await callback.answer()
    await callback.message.answer('Введите новый порог достижений:', reply_markup=cancel_button)
    await state.set_state(AdminStates.set_level)


@admin_router.message(AdminStates.set_level)
async def set_new_achievement(msg: Message, state: FSMContext):
    """Устанавливаем новый порог достижений"""
    try:
        await bot_base.set_new_setting('achievement', int(msg.text))
        settings_dict['achievement'] = int(msg.text)
        await msg.answer(f'Новый порог достижения в {msg.text} репутации(ий) установлен', reply_markup=main_menu)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка! Введите целое число:')


# --------------------
# Настройка уведомлений
# --------------------


@admin_router.callback_query(F.data == 'sett_notification')
async def notification_menu(callback: CallbackQuery):
    """Открываем меню доступных уведомлений"""
    await callback.answer()
    msg_text = (f'Установленные текста уведомлений:\n\n'
                f'<b>Получение благодарности от пользователя</b> - {settings_dict["new_gratitude"]}\n\n'
                f'<b>Преодоление порога достижения</b> - {settings_dict["new_achievement"]}\n\n'
                f'<b>Получение нового статуса</b> - {settings_dict["new_status"]}\n\n'
                f'<b>Начисление от администратора</b> - {settings_dict["admin_add"]}\n\n'
                f'<b>Списание баллов</b> - {settings_dict["admin_reduce"]}')
    await callback.message.answer(msg_text, reply_markup=notification_setting)


@admin_router.callback_query(F.data.startswith('notif_'))
async def start_notif_change(callback: CallbackQuery, state: FSMContext):
    """Ловим уведомление, которое хотят изменить"""
    await callback.answer()
    await state.set_state(AdminStates.sett_notification)
    await state.set_data({'notification': callback.data.replace('notif_', '')})
    await callback.message.answer('Введите новый текст уведомления:', reply_markup=cancel_button)


@admin_router.message(AdminStates.sett_notification)
async def catch_new_text_for_notification(msg: Message, state: FSMContext):
    """Ловим новый текст уведомления и сохраняем"""
    notif = (await state.get_data())['notification']
    settings_dict[notif] = msg.text
    await bot_base.set_new_setting(notif, msg.text)
    await msg.answer('Текст уведомления изменен!', reply_markup=main_menu)
    await state.clear()


# --------------------
# Настройка "благодарственного" списка
# --------------------


@admin_router.callback_query(F.data == 'sett_gratitude')
async def start_change_gratitude_list(callback: CallbackQuery):
    """Показываем список установленных слов, а так же кнопки удалить и добавить """
    await callback.answer()
    msg_text = 'Текущий список "благодарственных" слов:\n\n'
    for word in settings_dict['gratitude_list']:
        msg_text += word + '\n'
    await callback.message.answer(msg_text, reply_markup=gratitude_list_setting)


@admin_router.callback_query(F.data.startswith('gratitude_'))
async def choice_action_with_gratitude(callback: CallbackQuery, state: FSMContext):
    """Выбор действия со списком благодарностей"""
    await callback.answer()
    action_dict = {
        'gratitude_add': (AdminStates.gratitude_add, 'Введите новое слово:'),
        'gratitude_del': (AdminStates.gratitude_del, 'Введите слова которое хотите удалить')
    }
    await state.set_state(action_dict[callback.data][0])
    await callback.message.answer(action_dict[callback.data][1], reply_markup=cancel_button)


@admin_router.message(AdminStates.gratitude_add)
async def add_new_gratitude(msg: Message, state: FSMContext):
    """Добавление новой благодарности"""
    settings_dict['gratitude_list'].add(msg.text)
    await bot_base.add_gratitude_word(msg.text)
    await msg.answer('Новое слово добавлено!')
    msg_text = 'Текущий список "благодарственных" слов:\n\n'
    for word in settings_dict['gratitude_list']:
        msg_text += word + '\n'
    await msg.answer(msg_text)
    await state.clear()


@admin_router.message(AdminStates.gratitude_del)
async def remove_gratitude(msg: Message, state: FSMContext):
    """Удаление благодарности"""
    try:
        settings_dict['gratitude_list'].remove(msg.text)
    except KeyError:  # При попытке удалить то чего нет
        pass
    await bot_base.remove_gratitude_word(msg.text)
    await msg.answer('Слово удалено!')
    msg_text = 'Текущий список "благодарственных" слов:\n\n'
    for word in settings_dict['gratitude_list']:
        msg_text += word + '\n'
    await msg.answer(msg_text)
    await state.clear()

