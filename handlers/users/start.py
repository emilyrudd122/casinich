from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher import FSMContext
from keyboards.default import main_menu_user_keyboard
from keyboards.default import nickname_complete_keyboard
from utils.db_api import db
from states.register_user import register_user

from loader import dp

clear_keyboard = types.ReplyKeyboardRemove(selective=False)
# TODO: добавить проверку на админа и сделать отправление админу админ меню
@dp.message_handler(CommandStart(), state=None)
async def bot_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if db.check_user_exists(user_id):
        await message.answer("Главное меню", reply_markup=main_menu_user_keyboard)
    else:
        await register_user.get_nickname.set()
        
        await message.answer("Для регистрации укажите никнейм", reply_markup=clear_keyboard)

# сделать проверку никнейма на пригодность(не занят ли\ограничение на кол-во символов, на символы и тд)
@dp.message_handler(state=register_user.get_nickname)
async def get_user_nickname(message: types.Message, state: FSMContext):
    await register_user.complete_reg.set()
    async with state.proxy() as data:
        data['nickname'] = message.text
    await message.answer("Регистрируемся?", reply_markup=nickname_complete_keyboard)

@dp.message_handler(state=register_user.complete_reg)
async def complete_registration(message: types.Message, state: FSMContext):
    # Отмена
    if message.text.lower() == "зарегистрироваться":
        
        telegram_id = message.from_user.id
        
        async with state.proxy() as data:
            try:
                db.create_user(data['nickname'], telegram_id)
            except:
                print("smth went wrong(start)")
            print("user created")
        
        await message.answer("Вы успешно зарегистрированы", reply_markup=main_menu_user_keyboard)
        await state.finish()
    
    else:
        await register_user.get_nickname.set()
        await message.answer("Для регистрации укажите никнейм", reply_markup=clear_keyboard)
        
    
    