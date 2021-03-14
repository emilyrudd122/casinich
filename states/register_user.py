from aiogram.dispatcher.filters.state import StatesGroup, State


class register_user(StatesGroup):
    get_nickname = State()
    complete_reg = State()