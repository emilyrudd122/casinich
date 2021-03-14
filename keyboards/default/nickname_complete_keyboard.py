from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


nickname_complete_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Зарегистрироваться'),
            KeyboardButton(text='Отмена'),
        ],
    ],
    resize_keyboard=True
)