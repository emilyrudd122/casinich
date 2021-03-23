from aiogram.dispatcher.filters.state import StatesGroup, State


class promocode_check(StatesGroup):
    get_promocode = State()
    complete = State()