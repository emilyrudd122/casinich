from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import deposit_callback


deposit_check_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('Перейти к оплате', callback_data=deposit_callback.new(type="qiwi")),
        ],
        [
            InlineKeyboardButton('Проверить', callback_data=deposit_callback.new(type="check")),
            InlineKeyboardButton('Отменить оплату', callback_data=deposit_callback.new(type="cancel")),
        ]
    ]
)