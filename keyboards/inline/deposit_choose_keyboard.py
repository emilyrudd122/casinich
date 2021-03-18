from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import deposit_callback


deposit_choose_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('QIWI', callback_data=deposit_callback.new(type="qiwi")),
            InlineKeyboardButton('Промокод', callback_data=deposit_callback.new(type="promo")),
        ],
    ]
)