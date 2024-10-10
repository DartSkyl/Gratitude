from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder


# ========== Настройки ==========


all_settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Настройка званий', callback_data='set_status')],
    [InlineKeyboardButton(text='Установить порог достижения', callback_data='set_level')],
    [InlineKeyboardButton(text='Настройка уведомлений', callback_data='set_notification')],
    [InlineKeyboardButton(text='Словарь "благодарностей"', callback_data='set_gratitude')]
])

status_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Просмотреть/удалить звания', callback_data='status_view')],
    [InlineKeyboardButton(text='Добавить звание', callback_data='status_add')]
])

notification_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Получение благодарности', callback_data='notif_gratitude')],
    [InlineKeyboardButton(text='Достижение порога', callback_data='notif_level')],
    [InlineKeyboardButton(text='Начисление от администратора', callback_data='notif_from_admin')]
])

gratitude_list_setting = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Посмотреть/удалить список слов', callback_data='gratitude_view')],
    [InlineKeyboardButton(text='Добавить благодарность', callback_data='gratitude_add')]
])


async def view_status_list(status_dict: dict):
    """Возвращает клавиатуру для удаления статусов"""
    stat_list = InlineKeyboardBuilder()
    for points, status in status_dict.items():
        stat_list.button(text=f'Удалить статус "{status}"', callback_data=f'del_{points}')
    stat_list.adjust(1)
    return stat_list.as_markup()
