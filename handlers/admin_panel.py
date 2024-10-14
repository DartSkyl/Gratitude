from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from utils.admin_router import admin_router
from keyboards.admin_reply import *
from keyboards.admin_inline import *
from states import AdminStates
from loader import status_dict, bot_base, settings_dict, bot, app_run, app
from handlers.gratitude_checker import check_new_status, get_username
from utils.message_cleaner import message_cleaner

# from pyrogram import Client
#
# app = Client("gratitude_checker")

def escape_special_chars(text):
    """Экранирует все специальные символы в строке."""
    escaped = ''
    for char in text:
        if char in '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~':
            escaped += '\\' + char
        else:
            escaped += char
    return escaped


@admin_router.message(Command('start'))
async def start_function(msg: Message, state: FSMContext):
    """Функция запуска админпанели"""
    await state.clear()
    await msg.answer(f'Добрый день {msg.from_user.first_name}😀\nВыберете действие\:', reply_markup=main_menu)


@admin_router.message(F.text == '🚫 Отмена')
async def cancel_func(msg: Message, state: FSMContext):
    """Все отменяем и сбрасываем"""
    await state.clear()
    await msg.answer(f'Действие отменено\nВыберете действие\:', reply_markup=main_menu)


@admin_router.message(F.text == '⚙️ Настройки')
async def get_settings_menu(msg: Message):
    """Выводит меню настроек"""
    await msg.answer('Выберете настройку\:', reply_markup=all_settings)


@admin_router.callback_query(F.data.startswith('set_'))
async def choice_setting(callback: CallbackQuery):
    """Выбор настройки и запуск ее изменений"""
    await callback.answer()
    setting_dict = {
        'set_status': ('Выберете действие\:', status_setting),
        'set_level': (f'Порог достижения на данный момент {settings_dict["achievement"]} репутации', level_setting),
        'set_interval': (f'Интервал удаления сообщений установлен на '
                         f'{await message_cleaner.get_interval()} минут', interval_change)
    }
    await callback.message.answer(setting_dict[callback.data][0], reply_markup=setting_dict[callback.data][1])


# --------------------
# Настройка интервала и действующих чатов
# --------------------


@admin_router.callback_query(F.data == 'interval')
async def start_change_interval(callback: CallbackQuery, state: FSMContext):
    """Запуск изменения интервала"""
    await callback.answer()
    await callback.message.answer('Введите новое значение интервала\:', reply_markup=cancel_button)
    await state.set_state(AdminStates.interval)


@admin_router.message(AdminStates.interval)
async def set_interval(msg: Message, state: FSMContext):
    """Меняем значение интервала"""
    try:
        await message_cleaner.set_interval(int(msg.text))
        await msg.answer('Новый интервал установлен', reply_markup=main_menu)
        await bot_base.set_new_setting('interval', msg.text)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка\! Введите целое число\:')


@admin_router.callback_query(F.data == 'sett_chats')
async def get_chats_list(callback: CallbackQuery):
    """Открываем список чатов и выбор действия с ними"""
    await callback.answer()
    msg_text = 'Действующие чаты\:\n\n'
    for chat in settings_dict['chats']:
        ch = await bot.get_chat(chat)
        msg_text += f'{escape_special_chars(ch.title)}\n'
    await callback.message.answer(msg_text, reply_markup=chats_setting)


@admin_router.callback_query(F.data.startswith('chat_'))
async def choice_action_with_chat(callback: CallbackQuery, state: FSMContext):
    """Выбор действия с чатами"""
    await callback.answer()
    action_dict = {
        'chat_add': ('Вставьте ссылку формата https:\/\/t\.me\/chat\_username или id чата для добавления', AdminStates.chat_add),
        'chat_del': ('Вставьте ссылку формата https:\/\/t\.me\/chat\_username или id чата для удаления', AdminStates.chat_del)
    }
    await callback.message.answer(action_dict[callback.data][0], reply_markup=cancel_button)
    await state.set_state(action_dict[callback.data][1])


@admin_router.message(AdminStates.chat_add)
async def add_chat_to_bot(msg: Message, state: FSMContext):
    """Ловим ссылку для добавления чата и производим соответствующие операции"""
    try:
        if 'https' in msg.text:
            chat = msg.text.replace('https://t.me/', '@')
            chat = await bot.get_chat(chat)
        else:
            chat = await bot.get_chat(int(msg.text))
        settings_dict['chats'].add(chat.id)
        await bot_base.add_chat(chat.id)
        await state.clear()
        await msg.answer(f'Чат {chat.title} добавлен', reply_markup=main_menu)
    except Exception as e:
        await msg.answer('Ошибка ввода\!')
        print(e)


@admin_router.message(AdminStates.chat_del)
async def remove_chat_from_bot(msg: Message, state: FSMContext):
    """Ловим ссылку для удаления чата и производим соответствующие операции"""
    try:
        if 'https' in msg.text:
            chat = msg.text.replace('https://t.me/', '@')
            chat = await bot.get_chat(chat)
        else:
            chat = await bot.get_chat(int(msg.text))
        settings_dict['chats'].remove(chat.id)
        await bot_base.remove_chat(chat.id)
        await state.clear()
        await msg.answer(f'Чат {chat.title} удален', reply_markup=main_menu)
    except Exception as e:
        await msg.answer('Ошибка ввода\!')
        print(e)


# --------------------
# Управление статусами
# --------------------


@admin_router.callback_query(F.data.startswith('status_'))
async def status_management(callback: CallbackQuery, state: FSMContext):
    """Управление статусами"""
    await callback.answer()
    if callback.data == 'status_view':
        msg_text = 'Установленные статусы\:\n\n'
        for points_need, status_name in status_dict.items():
            msg_text += f'{status_name}: {points_need} очков\n'
        await callback.message.answer(msg_text, reply_markup=await view_status_list(status_dict))
        pass
    else:
        await state.set_state(AdminStates.status_add_name)
        await callback.message.answer('Введите название статуса\:', reply_markup=cancel_button)


@admin_router.message(AdminStates.status_add_name)
async def get_status_name(msg: Message, state: FSMContext):
    """Ловим название статуса"""
    await state.set_data({'status_name': msg.text})
    await state.set_state(AdminStates.status_add_points)
    await msg.answer('Введите число очков для достижения статуса\:')


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
        await msg.answer('Новый статус добавлен\!', reply_markup=main_menu)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка! Введите целое число\:')


@admin_router.callback_query(F.data.startswith('del_'))
async def remove_status(callback: CallbackQuery):
    """Удаляем статус"""
    rm_status = status_dict.pop(int(callback.data.replace('del_', '')))
    await bot_base.remove_status(rm_status)
    msg_text = 'Установленные статусы\:\n\n'
    for points_need, status_name in status_dict.items():
        msg_text += f'{status_name}\: {points_need} очков\n'
    await callback.message.edit_text(msg_text, reply_markup=await view_status_list(status_dict))


# --------------------
# Управление очками
# --------------------


@admin_router.message(F.text == '📋 Управление балансом')
async def balance_management_menu(msg: Message, state: FSMContext):
    """Открываем меню управления балансом пользователей"""
    await msg.answer('Введите @username пользователя\, над чьим балансом хотите провести манипуляцию\:')
    await state.set_state(AdminStates.select_user)


@admin_router.message(AdminStates.select_user)
async def select_user_for_manipulation(msg: Message, state: FSMContext):
    """Запоминаем выбранного юзера"""
    # await app.start()
    try:
        await app_run()
    except ConnectionError:
        pass
    user_id = (await app.get_users(msg.text)).id
    # await app.stop()
    try:
        user_info = await bot_base.get_user_info(user_id)
        msg_text = (f'Пользователь {msg.text}:\n'
                    f'Всего репутации получено: {user_info[1]}\n'
                    f'На балансе: {user_info[2]}\n'
                    f'Статус пользователя: {user_info[3]}')
    except IndexError:
        # Значит пользователя нет в базе
        msg_text = (f'Пользователь {msg.text}:\n'
                    f'Всего репутации получено: 0\n'
                    f'На балансе: 0\n'
                    f'Статус пользователя: None')

    await state.set_data({'uid': user_id, 'ufn': msg.text})
    await msg.answer(escape_special_chars(msg_text), reply_markup=balance_menu)


@admin_router.callback_query(AdminStates.select_user, F.data.startswith('balance_'))
async def user_balance_manipulation(callback: CallbackQuery, state: FSMContext):
    """Здесь начинается процесс изменения баланса пользователя"""
    await callback.answer()
    action_dict = {
        'balance_add': (AdminStates.balance_add, 'Введите количество репутации которое хотите добавить\:'),
        'balance_reduce': (AdminStates.balance_reduce, 'Введите количество баллов для списания\:'),
        'balance_rep_reduce': (AdminStates.balance_rep_reduce, 'Введите количество репутации для списания\:')
    }
    await callback.message.answer(action_dict[callback.data][1], reply_markup=cancel_button)
    await state.set_state(action_dict[callback.data][0])


@admin_router.message(AdminStates.balance_add)
async def user_balance_add(msg: Message, state: FSMContext):
    """Добавление баланса пользователю"""
    try:
        user = await state.get_data()
        user_id = (await state.get_data())['uid']
        await bot_base.add_points(user_id, int(msg.text))
        await msg.answer(f'Пользователю {user["ufn"]} начислено {msg.text} репутации', reply_markup=main_menu)
        await check_new_status(user_id)

        for chat in settings_dict['chats']:  # Ищем юзера по всем чатам и по этим же чатам и отправляем уведомление
            try:
                user_name = await get_username(chat, user_id)
                user = await bot_base.get_user_info(user_id)
                if user_name:
                    msg_text = f"""{settings_dict["admin_add"].format(
                        user_name=user_name,
                        user_rep=user[1],
                        user_points=user[2],
                        user_status=user[3] if user[3] else "Отсутствует",
                        add_points=msg.text,
                        reduce_points=0
                    )}"""
                    mess = await bot.send_message(chat_id=chat, text=msg_text)
                    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
            except Exception as e:
                print(e)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка\! Введите целое число\:')


@admin_router.message(AdminStates.balance_reduce)
async def user_balance_reduce(msg: Message, state: FSMContext):
    """Списание балов с баланса пользователя"""
    try:
        user = await state.get_data()
        user_id = (await state.get_data())['uid']
        await bot_base.reduce_user_balance(user_id, int(msg.text))
        await msg.answer(f'У пользователя {user["ufn"]} списано {msg.text} очков', reply_markup=main_menu)
        for chat in settings_dict['chats']:  # Ищем юзера по всем чатам и по этим же чатам и отправляем уведомление
            try:
                user_name = await get_username(chat, user_id)
                user = await bot_base.get_user_info(user_id)
                if user_name:
                    msg_text = f"""{settings_dict["admin_reduce"].format(
                        user_name=user_name,
                        user_rep=user[1],
                        user_points=user[2],
                        user_status=user[3] if user[3] else "Отсутствует",
                        add_points=0,
                        reduce_points=msg.text
                    )}"""
                    mess = await bot.send_message(chat_id=chat, text=msg_text)
                    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
            except Exception as e:
                print(e)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка\! Введите целое число\:')


@admin_router.message(AdminStates.balance_rep_reduce)
async def reduce_reputation(msg: Message, state: FSMContext):
    """Списание репутации с баланса пользователя"""
    try:
        from handlers.gratitude_checker import check_new_status
        user = await state.get_data()
        user_id = (await state.get_data())['uid']
        await bot_base.reduce_reputation(user_id, int(msg.text))
        await check_new_status(user_id)
        await msg.answer(f'У пользователя {user["ufn"]} списано {msg.text} репутации', reply_markup=main_menu)
        for chat in settings_dict['chats']:  # Ищем юзера по всем чатам и по этим же чатам и отправляем уведомление
            try:
                user_name = await get_username(chat, user_id)
                user = await bot_base.get_user_info(user_id)
                if user_name:
                    msg_text = f"""{settings_dict["admin_rep_reduce"].format(
                        user_name=user_name,
                        user_rep=user[1],
                        user_points=user[2],
                        user_status=user[3] if user[3] else "Отсутствует",
                        add_points=0,
                        reduce_points=msg.text
                    )}"""
                    mess = await bot.send_message(chat_id=chat, text=msg_text)
                    await message_cleaner.schedule_message_deletion(mess.chat.id, mess.message_id)
            except Exception as e:
                print(e, e.args)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка\! Введите целое число\:')


# --------------------
# Установка порога достижения
# --------------------


@admin_router.callback_query(F.data == 'level_set')
async def change_achievement(callback: CallbackQuery, state: FSMContext):
    """Запускаем изменения порога достижений"""
    await callback.answer()
    await callback.message.answer('Введите новый порог достижений\:', reply_markup=cancel_button)
    await state.set_state(AdminStates.set_level)


@admin_router.message(AdminStates.set_level)
async def set_new_achievement(msg: Message, state: FSMContext):
    """Устанавливаем новый порог достижений"""
    try:
        await bot_base.set_new_setting('achievement', int(msg.text))
        settings_dict['achievement'] = int(msg.text)
        await msg.answer(f'Новый порог достижения в {msg.text} репутации\(ий\) установлен', reply_markup=main_menu)
        await state.clear()
    except ValueError:
        await msg.answer('Ошибка\! Введите целое число\:')


# --------------------
# Настройка уведомлений
# --------------------


@admin_router.callback_query(F.data == 'sett_notification')
async def notification_menu(callback: CallbackQuery):
    """Открываем меню доступных уведомлений"""
    await callback.answer()
    msg_text = (f'Установленные текста уведомлений\n\n'
                f'*Получение благодарности от пользователя*\:\n{settings_dict["new_gratitude"]}\n\n'
                f'*Преодоление порога достижения*\:\n{settings_dict["new_achievement"]}\n\n'
                f'*Получение нового статуса*\:\n{settings_dict["new_status"]}\n\n'
                f'*Просмотр статистики*\:\n{settings_dict["karma"]}\n\n'
                f'*Начисление от администратора*\:\n{settings_dict["admin_add"]}\n\n'
                f'*Рейтинг чата*\:\n{settings_dict["rating"]}\n\n'
                f'*Списание репутации*\:\n{settings_dict["admin_rep_reduce"]}\n\n'
                f'*Списание баллов*\:\n{settings_dict["admin_reduce"]}').format(
        user_name='@UserName',
        user_rep=10,
        user_points=5,
        user_status='Царь всея чата',
        add_points=2,
        reduce_points=3
    )
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
    try:
        notif = (await state.get_data())['notification']
        new_notif_text = msg.md_text.replace('\{', '{')
        new_notif_text = new_notif_text.replace('\}', '}')
        new_notif_text = new_notif_text.replace('\_', '_')
        settings_dict[notif] = new_notif_text
        msg_text = (f'Установленные текста уведомлений\n\n'
                    f'*Получение благодарности от пользователя*\:\n{settings_dict["new_gratitude"]}\n\n'
                    f'*Преодоление порога достижения*\:\n{settings_dict["new_achievement"]}\n\n'
                    f'*Получение нового статуса*\:\n{settings_dict["new_status"]}\n\n'
                    f'*Просмотр статистики*\:\n{settings_dict["karma"]}\n\n'
                    f'*Начисление от администратора*\:\n{settings_dict["admin_add"]}\n\n'
                    f'*Рейтинг чата*\:\n{settings_dict["rating"]}\n\n'
                    f'*Списание репутации*\:\n{settings_dict["admin_rep_reduce"]}\n\n'
                    f'*Списание баллов*\:\n{settings_dict["admin_reduce"]}').format(
            user_name='@UserName',
            user_rep=10,
            user_points=5,
            user_status='Царь всея чата',
            add_points=2,
            reduce_points=3
        )
        await bot_base.set_new_setting(notif, new_notif_text)
        await msg.answer('Текст уведомления изменен\!', reply_markup=main_menu)
        await msg.answer(msg_text, reply_markup=notification_setting)
        await state.clear()
    except Exception as e:
        await msg.answer('Ошибка вода\!')
        print(e.args)
        print(e)


# --------------------
# Настройка "благодарственного" списка
# --------------------


@admin_router.callback_query(F.data == 'sett_gratitude')
async def start_change_gratitude_list(callback: CallbackQuery):
    """Показываем список установленных слов, а так же кнопки удалить и добавить """
    await callback.answer()
    msg_text = 'Текущий список \"благодарственных\" слов:\n\n'
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
    await msg.answer('Новое слово добавлено\!')
    msg_text = 'Текущий список \"благодарственных\" слов:\n\n'
    for word in settings_dict['gratitude_list']:
        msg_text += escape_special_chars(word) + '\n'
    await msg.answer(msg_text, reply_markup=cancel_button)
    await state.clear()


@admin_router.message(AdminStates.gratitude_del)
async def remove_gratitude(msg: Message, state: FSMContext):
    """Удаление благодарности"""
    try:
        settings_dict['gratitude_list'].remove(msg.text)
    except KeyError:  # При попытке удалить то чего нет
        pass
    await bot_base.remove_gratitude_word(msg.text)
    await msg.answer('Слово удалено\!')
    msg_text = 'Текущий список "благодарственных" слов:\n\n'
    for word in settings_dict['gratitude_list']:
        msg_text += word + '\n'
    await msg.answer(msg_text)
    await state.clear()


@admin_router.message(Command('get_settings'))
async def output_settings_from_db(msg: Message, command: CommandObject):
    """Выводит список настроек из БД (отладочная функция)"""
    if not command.args:
        settings_list = await bot_base.get_all_settings()
        msg_text = ''
        for s in settings_list:
            msg_text += f'{s[0]}: {s[1]}\n\n'
        await msg.answer(escape_special_chars(msg_text))
    else:
        try:
            await bot_base.drop_setting(command.args)
        except Exception as e:
            await msg.answer(str(e))
