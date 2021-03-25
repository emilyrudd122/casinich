from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
# from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from states.create_game import create_game
from keyboards.default import main_menu_user_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.inline.callback_datas import games_callback, games_play_callback
from utils import get_new_card


from utils.db_api import db

from data import config
import aiogram.utils.markdown as md

from loader import dp, bot

# TODO: подшлифовать все надписи в отправляемых сообщениях

async def game_win_check(game_id):
    # print("work")
    game_obj = db.get_game(game_id)
    host = game_obj['host_sum']
    player = game_obj['player_sum']
    async def host_win():
        # выиграл хост
        db.add_game(game_obj['telegram_id_host'], 1)
        db.change_user_rub_balance(game_obj['telegram_id_host'], (int(game_obj['bet_amount'])*2))
        await bot.send_message(
            game_obj['telegram_id_host'],
            "Вы выиграли! Поздравляем вам на счет начислено %s рублей" % (int(game_obj['bet_amount'])*2)
        )
        db.add_game(game_obj['telegram_id_player'], 0)
        await bot.send_message(
            game_obj['telegram_id_player'],
            "Вы проиграли. -%s рублей" % game_obj['bet_amount']
        )
    async def player_win():
        # выиграл плеер
        db.add_game(game_obj['telegram_id_player'], 1)
        await bot.send_message(
            game_obj['telegram_id_host'],
            "Вы проиграли. -%s рублей" % game_obj['bet_amount']
        )
        db.add_game(game_obj['telegram_id_host'], 0)
        db.change_user_rub_balance(game_obj['telegram_id_player'], (int(game_obj['bet_amount'])*2))
        await bot.send_message(
            game_obj['telegram_id_player'],
            "Вы выиграли! Поздравляем вам на счет начислено %s рублей" % (int(game_obj['bet_amount'])*2)
        )
    async def draw():
        # ничья
        db.add_game(game_obj['telegram_id_host'], 0)
        db.add_game(game_obj['telegram_id_player'], 0)
        db.change_user_rub_balance(game_obj['telegram_id_host'], (int(game_obj['bet_amount'])))
        await bot.send_message(
            game_obj['telegram_id_host'],
            "Ничья! Вам возращено %s рублей." % (int(game_obj['bet_amount'])*2)
        )
        db.change_user_rub_balance(game_obj['telegram_id_player'], int(game_obj['bet_amount']))
        await bot.send_message(
            game_obj['telegram_id_player'],
            "Ничья! Вам возращено %s рублей." % (int(game_obj['bet_amount'])*2)
        )
    async def both_lost():
        db.add_game(game_obj['telegram_id_player'], 0)
        db.add_game(game_obj['telegram_id_host'], 0)
        await bot.send_message(
            game_obj['telegram_id_host'],
            "Вы проиграли. -%s рублей" % game_obj['bet_amount']
        )
        await bot.send_message(
            game_obj['telegram_id_player'],
            "Вы проиграли. -%s рублей" % game_obj['bet_amount']
        )
    if host < 22 and player > 22:
        db.set_game_winner(game_id, "host")
        await host_win()
    elif host > 22 and player < 22:
        db.set_game_winner(game_id, "player")
        await player_win()
    elif host > 22 and player > 22:
        db.set_game_winner(game_id, "lost")
        await both_lost()
    elif host == player:
        db.set_game_winner(game_id, "draw")
        await draw()
    elif (host < 22 and player < 22) and host < player:
        db.set_game_winner(game_id, "player")
        await player_win()
    elif (host < 22 and player < 22) and host > player:
        db.set_game_winner(game_id, "host")
        await host_win()
    

cards_value = {
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'jack': 2,
    'queen': 3,
    'king': 4,
}

clear_keyboard = types.ReplyKeyboardRemove(selective=False)
# TODO: сделать отображение игр, где соперник еще не закончил набор карт.
# TODO: сделать отображение игр, которые созданы хостом. сделать возможность их отмены
# TODO: сделать кнопку обновить работающей
# DONE: сделать проверку, чтобы сумма игры была числом
@dp.message_handler(lambda message: message.text.lower() == "игры")
async def cabinet_handler(message: types.Message):
    user_id = message.from_user.id
    user = db.check_user_exists(user_id)
    if not user:
        await message.answer("you are not registered, type /start")
        return
    # TODO: сделать пагинацию по играм
    txt = "Созданных игр пока нет. Можете создать свою по кнопкам ниже."
    games_keyboard = InlineKeyboardMarkup(row_width=2)
    games = db.get_new_games()
    if games:    
        for g in games:
            if g['telegram_id_host'] != user_id:
                games_keyboard.insert(InlineKeyboardButton(f"игра #{g['id']} на {g['bet_amount']} рублей", callback_data=games_play_callback.new(type="game_preview", number=g['id'])))
        txt = "Доступные игры:"
        games_keyboard.add(InlineKeyboardButton("Обновить", callback_data=games_callback.new(type="refresh")))


    k1 = InlineKeyboardButton('Создать игру[Рубли]', callback_data=games_callback.new(type="create_rubles"))
    k2 = InlineKeyboardButton('Создать игру[Баллы]', callback_data=games_callback.new(type="create_points"))
    k3 = InlineKeyboardButton('Ваши игры', callback_data=games_callback.new(type="user_games"))
    k4 = InlineKeyboardButton('Текущие игры', callback_data=games_callback.new(type="user_playing_games"))
    games_keyboard.add(k1, k2)
    games_keyboard.add(k3, k4)
    # games_keyboard = InlineKeyboardMarkup(
    #     inline_keyboard=[
    #         [
    #             InlineKeyboardButton('Создать игру[Рубли]', callback_data=games_callback.new(type="create_rubles")),
    #             InlineKeyboardButton('Создать игру[Баллы]', callback_data=games_callback.new(type="create_points")),
    #         ]
    #     ]
    # )
    
    await message.answer(
        txt,
        reply_markup=games_keyboard
    )

@dp.callback_query_handler(games_play_callback.filter(type="back"))
async def back_query_handler(call: types.CallbackQuery):
    
    user_id = call.from_user.id
    txt = "Созданных игр пока нет. Можете создать свою по кнопкам ниже."
    games_keyboard = InlineKeyboardMarkup(row_width=2)
    games = db.get_new_games()
    if games:    
        for g in games:
            if g['telegram_id_host'] != user_id:
                games_keyboard.insert(InlineKeyboardButton(f"игра #{g['id']} на {g['bet_amount']} рублей", callback_data=games_play_callback.new(type="game_preview", number=g['id'])))
        txt = "Доступные игры:"
        games_keyboard.add(InlineKeyboardButton("Обновить", callback_data=games_callback.new(type="refresh")))


    k1 = InlineKeyboardButton('Создать игру[Рубли]', callback_data=games_callback.new(type="create_rubles"))
    k2 = InlineKeyboardButton('Создать игру[Баллы]', callback_data=games_callback.new(type="create_points"))      
    games_keyboard.add(k1, k2)
    await call.message.delete()
    await call.message.answer(
        txt,
        reply_markup=games_keyboard
    )    


@dp.callback_query_handler(games_play_callback.filter(type="game_preview"))
async def show_game_preview_handler(call: types.CallbackQuery, callback_data:dict):
    await call.answer(cache_time=1)
    await call.message.delete()
    game_id = callback_data.get("number")
    game_obj = db.get_game(game_id)
    
    play_or_not_keyboard = InlineKeyboardMarkup(row_width=2)
    k1 = InlineKeyboardButton('Играть', callback_data=games_play_callback.new(type="game_start", number=game_obj['id']))
    k2 = InlineKeyboardButton('Назад', callback_data=games_play_callback.new(type="back", number="back"))
    play_or_not_keyboard.add(k1, k2)
    
    # await call.message.delete()
    await call.message.answer(f"game_id={game_obj['id']}\nbet_amount={game_obj['bet_amount']}\ncreated by(id)={game_obj['telegram_id_host']}", reply_markup=play_or_not_keyboard)
    
@dp.callback_query_handler(games_play_callback.filter(type="game_start"))
async def game_start_query_handler(call: types.CallbackQuery, callback_data:dict):
    await call.message.delete()
    
    game_id = callback_data.get("number")
    user_id = call.from_user.id
    player_add_to_game = db.add_player_to_game(game_id, user_id)
    
    if not player_add_to_game:
        await call.message.answer("smth went wrong. contact admin")
        return

    game_obj = db.get_game(game_id)
    sum = -int(game_obj['bet_amount'])
    db.change_user_rub_balance(user_id, sum)
    await bot.send_message(
        game_obj['telegram_id_host'],
        f"{user_id} присоединился к игре #{game_obj['id']}, ожидайте свой ход."
    )
    game_keyboard = InlineKeyboardMarkup(row_width=2)
    k1 = InlineKeyboardButton('Взять еще карту', callback_data=games_play_callback.new(type="plus_card", number=game_obj['id']))
    k2 = InlineKeyboardButton('Хватит, вскрываемся', callback_data=games_play_callback.new(type="stop_card", number=game_obj['id']))
    game_keyboard.add(k1, k2)
    if int(user_id) == int(game_obj['telegram_id_host']):
        await call.message.answer(f"Количество карт: {game_obj['host_cards']}\nКоличество очков: {game_obj['host_sum']}", reply_markup=game_keyboard)
    else:
        await call.message.answer(f"Количество карт: {game_obj['player_cards']}\nКоличество очков: {game_obj['player_sum']}", reply_markup=game_keyboard)
    
@dp.callback_query_handler(games_play_callback.filter(type="plus_card"))
async def plus_card_query_handler(call: types.CallbackQuery, callback_data:dict):
    user_id = call.from_user.id
    game_id = callback_data.get("number")
    game_obj = db.get_game(game_id)
    
    game_keyboard = InlineKeyboardMarkup(row_width=2)
    k1 = InlineKeyboardButton('Взять еще карту', callback_data=games_play_callback.new(type="plus_card", number=game_obj['id']))
    k2 = InlineKeyboardButton('Хватит, вскрываемся', callback_data=games_play_callback.new(type="stop_card", number=game_obj['id']))
    game_keyboard.add(k1, k2)
    if int(user_id) == int(game_obj['telegram_id_host']):
        card = get_new_card.create_card()
        if card == 'ace':
            if game_obj['host_cards'] == 0 or game_obj['host_cards']:
                points=10
            else:
                points=1
        try:
            points = cards_value[card]
        except KeyError:
            pass
        db.add_card_host(game_id)
        db.add_sum_host(game_id, points)
        if game_obj['host_sum'] + points > 21:
            await call.message.edit_text(
                f"Новая карта - {card}\nКоличество карт: {int(game_obj['host_cards'])+1}\nКоличество очков: {int(game_obj['host_sum'])+int(points)}",
            )
            # await call.message.answer("У вас больше 21го - вы проиграли =(")
            await game_win_check(game_id)
            return
        await call.message.edit_text(
            f"Новая карта - {card}\nКоличество карт: {int(game_obj['host_cards'])+1}\nКоличество очков: {int(game_obj['host_sum'])+int(points)}",
            reply_markup=game_keyboard,
        )
        
    else:
        card = get_new_card.create_card()
        if card == 'ace':
            if game_obj['player_cards'] == 0 or game_obj['player_cards'] == 1:
                points=10
            else:
                points=1
        try:
            points = cards_value[card]
        except KeyError:
            pass
        db.add_card_player(game_id)
        db.add_sum_player(game_id, points)
        if game_obj['player_sum'] + points > 21:
            await call.message.edit_text(
                f"Новая карта - {card}\nКоличество карт: {int(game_obj['player_cards'])+1}\nКоличество очков: {int(game_obj['player_sum'])+int(points)}"
            )
            await call.message.answer("У вас больше 21го - вы проиграли =(")

            await bot.send_message(
                game_obj['telegram_id_host'],
                f"Количество карт: {game_obj['host_cards']}\nКоличество очков: {game_obj['host_sum']}",
                reply_markup=game_keyboard
            )
            return        

        await call.message.edit_text(
            f"Новая карта - {card}\nКоличество карт: {int(game_obj['player_cards'])+1}\nКоличество очков: {int(game_obj['player_sum'])+int(points)}",
            reply_markup=game_keyboard,
        )


        
@dp.callback_query_handler(games_play_callback.filter(type="stop_card"))
async def stop_take_cards_handler(call: types.CallbackQuery, callback_data: dict):
    user_id = call.from_user.id
    game_id = callback_data.get("number")
    game_obj = db.get_game(game_id)
    
    if user_id != game_obj['telegram_id_host']:
        game_keyboard = InlineKeyboardMarkup(row_width=2)
        k1 = InlineKeyboardButton('Взять еще карту', callback_data=games_play_callback.new(type="plus_card", number=game_obj['id']))
        k2 = InlineKeyboardButton('Хватит, вскрываемся', callback_data=games_play_callback.new(type="stop_card", number=game_obj['id']))
        game_keyboard.add(k1, k2)
        db.make_player_done(game_id)
        await bot.send_message(
            game_obj['telegram_id_host'],
            f"Количество карт: {game_obj['host_cards']}\nКоличество очков: {game_obj['host_sum']}",
            reply_markup=game_keyboard
        )
        await call.message.answer("Ожидайте второго игрока.")
    
    else:
        db.make_host_done(game_id)
        await game_win_check(game_id)
        return
                  
            

@dp.callback_query_handler(games_callback.filter(type="create_rubles"))
async def game_create_rubles_handler(call: types.CallbackQuery):
    await call.answer(cache_time=10)
    # await call.answer("💵 Укажите на какую сумму будет игра:")
    test = InlineKeyboardMarkup()
    await call.message.edit_text(
        "💵 Укажите на какую сумму будет игра:",
        reply_markup=test
    )
    await create_game.get_sum.set()
    
@dp.message_handler(state=create_game.get_sum)
async def get_rubles_game_bet_amount_handler(message: types.Message, state:FSMContext):
    bet_amount = ""
    try:
        bet_amount = int(message.text)
    except:
        await message.answer("Ставка должна быть числом, попробуйте еще раз")
        return
    await create_game.complete_creation.set()
    async with state.proxy() as data:
        data['bet_amount'] = bet_amount
    await message.answer(f"❕ Ваша ставка {bet_amount} рублей, для подтверждения отправьте +")

@dp.message_handler(state=create_game.complete_creation)
async def rubles_game_complete_creation_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if message.text == "+":
        async with state.proxy() as data:
            if db.create_game_rub(user_id, data['bet_amount']):
                await message.answer("✅ Игра создана. Ожидайте соперника...", reply_markup=main_menu_user_keyboard)
            else:
                await message.answer("Ваш баланс меньше чем сумма ставки")    
        await state.finish()
        return
    
    await message.answer("Игра отменена", reply_markup=main_menu_user_keyboard)
    await state.finish()
    