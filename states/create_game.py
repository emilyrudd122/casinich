from aiogram.dispatcher.filters.state import StatesGroup, State


class create_game(StatesGroup):
    get_sum = State()
    complete_creation = State()