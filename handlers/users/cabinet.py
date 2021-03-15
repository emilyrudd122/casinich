from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext
from keyboards.default import main_menu_user_keyboard
from utils.db_api import db
import aiogram.utils.markdown as md

from loader import dp

clear_keyboard = types.ReplyKeyboardRemove(selective=False)
@dp.message_handler(lambda message: message.text.lower() == "кабинет", state=None)
async def cabinet_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.check_user_exists(user_id)
    if not user:
        await message.answer("you are not registered, type /start")
        return
    
    await message.answer(
        md.text(
            md.text("id: " + str(user['telegram_id'])),
            md.text("Баланс [Рубли]: " + str(user['balance_rub'])),
            md.text("Баланс [Баллы]: " + str(user['balance_points'])),
            md.text(),
            md.text("Статистика:"),
            md.text(),
            md.text("Игры: " + str(user['games'])),
            md.text("Победы: " + str(user['wins'])),
            md.text("Проигрыши: " + str(int(user['games']) - int(user['wins']))),
            sep='\n',
        )
    )