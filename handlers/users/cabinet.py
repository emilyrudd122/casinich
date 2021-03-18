from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
# from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from keyboards.default import main_menu_user_keyboard
from keyboards.inline import cabinet_keyboard, deposit_choose_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import cabinet_callback, deposit_callback
from utils.db_api import db
from utils import check_payment
from data import config
import aiogram.utils.markdown as md

from loader import dp

clear_keyboard = types.ReplyKeyboardRemove(selective=False)

def cabinet_message(user):
    msg_text = md.text(
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
    return msg_text

def payment_message(qiwi_number, code):
    msg_text = md.text(
            md.text("Пополнение QIWI:"),
            md.text("➖➖➖➖➖➖➖➖"),
            md.text("👉 Номер " + str(qiwi_number)),
            md.text("👉 Коментарий " + str(code)),
            md.text(),
            md.text("⚠️ Минимальная сумма пополнения 10₽"),
            md.text("⚠️ Обязательно указывайте комментарий!"),
            sep='\n',
        )
    return msg_text

clear_keyboard = types.ReplyKeyboardRemove(selective=False)
@dp.message_handler(lambda message: message.text.lower() == "кабинет", state=None)
async def cabinet_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.check_user_exists(user_id)
    if not user:
        await message.answer("you are not registered, type /start")
        return
    
    await message.answer(
        cabinet_message(user),
        reply_markup=cabinet_keyboard
    )
    
@dp.callback_query_handler(cabinet_callback.filter(action="points"))
async def get_points_handler(call: types.CallbackQuery):
    # await call.answer(cache_time=3600)
    
    #TODO: добавить проверку на дату последнего получения баллов юзером
    
    # def check_last_time_take_points():
    #     pass
    
    # if not check_last_time_take_points():
    #     return
    
    user_id = call.from_user.id
    db.add_points(user_id)
    user = db.check_user_exists(user_id)
    await call.message.edit_text(
        cabinet_message(user),
        reply_markup=cabinet_keyboard
    )


@dp.callback_query_handler(cabinet_callback.filter(action="deposit"))
async def deposit_handler(call: types.CallbackQuery):
    await call.message.edit_text(
        "Выбери способ для депозита",
        reply_markup=deposit_choose_keyboard,
    )
    


# TODO: добавить хандлер для промокодов
# TODO: добавить хандлер для вывода средств

@dp.callback_query_handler(deposit_callback.filter(type="qiwi"))
async def qiwi_deposit_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    db.create_payment(user_id)
    
    code = user_id
    payment_url = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={config.QIWI_NUMBER}&amountFraction=0&extra%5B%27comment%27%5D={code}&currency=643&&blocked[0]=account&&blocked[1]=comment"
    
    deposit_check_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('Перейти к оплате', url=payment_url),
            ],
            [
                InlineKeyboardButton('Проверить', callback_data=deposit_callback.new(type="check")),
                InlineKeyboardButton('Отменить оплату', callback_data=deposit_callback.new(type="cancel")),
            ]
        ]
    )
    
    await call.message.edit_text(
        payment_message(config.QIWI_NUMBER, db.check_old_payments(user_id)),
        reply_markup=deposit_check_keyboard,
    )
    
    
@dp.callback_query_handler(deposit_callback.filter(type="check"))
async def qiwi_deposit_check_handler(call: types.CallbackQuery):
    await call.answer(cache_time=10)
    user_id = call.from_user.id
    code = db.check_old_payments(user_id)
    if not code:
        #TODO: отправить что у пользователя неt платежа(error)
        pass
    
    amount = check_payment(code)
    # TODO: подумать как вынести эту клавиатуру в отдельный файл(мб использовать middlewares куда будет подгружаться инстанс юзера и соотв оттуда брать код для ссылки)
    if not amount:
        payment_url = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={config.QIWI_NUMBER}&amountFraction=0&extra%5B%27comment%27%5D={code}&currency=643&&blocked[0]=account&&blocked[1]=comment"
    
        deposit_check_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton('Перейти к оплате', url=payment_url),
                ],
                [
                    InlineKeyboardButton('Проверить', callback_data=deposit_callback.new(type="check")),
                    InlineKeyboardButton('Отменить оплату', callback_data=deposit_callback.new(type="cancel")),
                ]
            ]
        )
        msg = md.text(
            md.text("⚠️Пока что платеж не получен"),
            md.text("➖➖➖➖➖➖➖➖"),
            md.text("👉 Номер " + str(config.QIWI_NUMBER)),
            md.text("👉 Коментарий " + str(code)),
            md.text(),
            md.text("⚠️ Минимальная сумма пополнения 10₽"),
            md.text("⚠️ Обязательно указывайте комментарий!"),
            sep='\n',
        )
        await call.message.edit_text(
            msg,
            reply_markup=deposit_check_keyboard,
        )
        # return
    
    else:
        db.set_sum_payment(user_id, amount)
        db.change_payment_status(user_id, "done")
        db.change_user_rub_balance(user_id, amount)
        await call.message.edit_text(
            'Платеж получен! Баланс пополнен на ' + int(amount),
        )

# TODO: make cancel button work
@dp.callback_query_handler(deposit_callback.filter(type="cancel"))
async def qiwi_deposit_cancel_handler(call:types.CallbackQuery):
    await call.answer(cache_time=10)
    
    