from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import cabinet_callback


cabinet_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('Получить баллы(доступно каждый час)', callback_data=cabinet_callback.new(action="points")),
        ],
        [
            InlineKeyboardButton('Пополнить баланс', callback_data=cabinet_callback.new(action="deposit")),
            InlineKeyboardButton('Вывод средств', callback_data=cabinet_callback.new(action="withdraw")),
        ],
        [
            InlineKeyboardButton('Реферальная система', callback_data=cabinet_callback.new(action="refsystem")),
        ]
    ]
)