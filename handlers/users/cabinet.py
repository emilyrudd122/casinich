from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
# from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from keyboards.default import main_menu_user_keyboard, cancel_keyboard
from keyboards.inline import cabinet_keyboard, deposit_choose_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import cabinet_callback, deposit_callback
from utils.db_api import db
from utils import check_payment
from data import config
import aiogram.utils.markdown as md
from states.promocode_check import promocode_check
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

# DONE: добавить хандлер для промокодов    
@dp.callback_query_handler(deposit_callback.filter(type="promo"))
async def promo_deposit_handler(call: types.CallbackQuery):
    await promocode_check.get_promocode.set()
    await call.message.answer("Введите промокод:", reply_markup=cancel_keyboard)
    
@dp.message_handler(state=promocode_check.get_promocode)
async def promo_check_handler(message: types.Message, state: FSMContext):
    promocode = message.text
    if promocode == "Отмена":
        await state.finish()
        await message.answer(
            f"Ввод промокода отменен",
            reply_markup=main_menu_user_keyboard
        )
        return
    p_c = db.get_promo(promocode)
    if not p_c:
        await message.answer("Такого промокода нет. Попробуйте еще раз.")
        return
    async with state.proxy() as data:
        data['code'] = promocode
    if p_c['used'] == 0:
        await promocode_check.complete.set()
        prom_amount = p_c['amount']
        await message.answer(
            f"Вы уверены что хотите применить промокод на {p_c['amount']}?\nДля подтверждения отправьте +"
        )
    else:
        await message.answer(
            f"Промокод №{promocode} уже использован. Если вы этого не делали, то свяжитесь с администрацией. Контакты указаны в разделе информация.",
            reply_markup=main_menu_user_keyboard
        )
        await state.finish()
    
@dp.message_handler(state=promocode_check.complete)
async def promo_complete_handler(message: types.Message, state: FSMContext):
    answer = message.text
    user_id = message.from_user.id
    
    if answer == "Отмена":
        await state.finish()
        await message.answer(
            f"Ввод промокода отменен",
            reply_markup=main_menu_user_keyboard
        )
        return

    if answer == "+":
        async with state.proxy() as data:
            promo = db.get_promo(data['code'])
            db.change_user_rub_balance(user_id, promo['amount'])
            sum = promo['amount']
            await message.answer(
                f"Вам на баланс было начислено {sum}. Желаем приятной игры!",
                reply_markup=main_menu_user_keyboard
            )
            db.make_promo_used(data['code'])
            await state.finish()
    else:
        await state.finish()
        await message.answer(
            f"Ввод промокода отменен",
            reply_markup=main_menu_user_keyboard
        )
        return
    


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
    
    