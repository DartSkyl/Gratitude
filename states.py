from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    notif_gratitude = State()
    notif_level = State()
    notif_from_admin = State()
    status_add_name = State()
    status_add_points = State()
    gratitude_add = State()
