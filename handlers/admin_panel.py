from aiogram.types import Message, CallbackQuery
from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.admin_router import admin_router
from keyboards.admin_reply import *
from keyboards.admin_inline import *
from states import AdminStates
from loader import status_dict, bot_base


@admin_router.message(Command('start'))
async def start_function(msg: Message):
    """Функция запуска админпанели"""
    await msg.answer(f'Добрый день <b>{msg.from_user.first_name}</b>😀\nВыберете действие:', reply_markup=main_menu)


@admin_router.message(F.text == '⚙️ Настройки')
async def get_settings_menu(msg: Message):
    """Выводит меню настроек"""
    await msg.answer('Выберете настройку:', reply_markup=all_settings)


@admin_router.callback_query(F.data.startswith('set_'))
async def choice_setting(callback: CallbackQuery):
    """Выбор настройки и запуск ее изменений"""
    await callback.answer()
    settings_dict = {
        'set_status': ('Выберете действие:', status_setting),
        'set_level': ('Введите порог достижения:', None),
        'set_notification': ('Выберете уведомление для изменения:', notification_setting),
        'set_gratitude': ('Выберете действие:', gratitude_list_setting)
    }
    await callback.message.answer(settings_dict[callback.data][0], reply_markup=settings_dict[callback.data][1])


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
