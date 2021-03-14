from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu_user_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Игры'),
        ],
        [
            KeyboardButton(text='Кабинет'),
            KeyboardButton(text='Информация'),
        ]
        
    ],
    resize_keyboard=True
)