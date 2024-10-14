from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


# ========== Настройки ==========


all_settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Настройка званий', callback_data='set_status')],
    [InlineKeyboardButton(text='Настройка интервала удаления сообщений', callback_data='set_interval')],
    [InlineKeyboardButton(text='Порог достижения', callback_data='set_level')],
    [InlineKeyboardButton(text='Настройка уведомлений', callback_data='sett_notification')],  # sett
    [InlineKeyboardButton(text='Список "благодарностей"', callback_data='sett_gratitude')],  # sett
    [InlineKeyboardButton(text='Действующие чаты', callback_data='sett_chats')]  # sett
])

chats_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить чат', callback_data='chat_add')],
    [InlineKeyboardButton(text='Удалить чат', callback_data='chat_del')]
])

interval_change = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить интервал', callback_data='interval')],
])

level_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить порог достижения', callback_data='level_set')],
])


status_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Просмотреть/удалить звания', callback_data='status_view')],
    [InlineKeyboardButton(text='Добавить звание', callback_data='status_add')]
])

notification_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Изменить "Получение благодарности"', callback_data='notif_new_gratitude')],
    [InlineKeyboardButton(text='Изменить "Достижение порога"', callback_data='notif_new_achievement')],
    [InlineKeyboardButton(text='Изменить "Получение нового статуса"', callback_data='notif_new_status')],
    [InlineKeyboardButton(text='Изменить "Просмотр статистики"', callback_data='notif_karma')],
    [InlineKeyboardButton(text='Изменить "Начисление от администратора"', callback_data='notif_admin_add')],
    [InlineKeyboardButton(text='Изменить "Рейтинг чата"', callback_data='notif_rating')],
    [InlineKeyboardButton(text='Изменить "Списание репутации администратором"', callback_data='notif_admin_rep_reduce')],
    [InlineKeyboardButton(text='Изменить "Списание балов администратором"', callback_data='notif_admin_reduce')]
])

gratitude_list_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить благодарность', callback_data='gratitude_add')],
    [InlineKeyboardButton(text='Удалить благодарность', callback_data='gratitude_del')]

])


async def view_status_list(status_dict: dict):
    """Возвращает клавиатуру для удаления статусов"""
    stat_list = InlineKeyboardBuilder()
    for points, status in status_dict.items():
        stat_list.button(text=f'Удалить звание "{status}"', callback_data=f'del_{points}')
    stat_list.adjust(1)
    return stat_list.as_markup()


# ========== Управление балансом ==========

balance_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начислить очки', callback_data='balance_add')],
    [InlineKeyboardButton(text='Списать очки', callback_data='balance_reduce')],
    [InlineKeyboardButton(text='Списать репутацию', callback_data='balance_rep_reduce')]
])
