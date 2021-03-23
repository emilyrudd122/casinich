from aiogram.utils.callback_data import CallbackData

cabinet_callback = CallbackData("cabinet", "action")
deposit_callback = CallbackData("deposit", "type")
games_callback = CallbackData("games", "type")
games_play_callback = CallbackData("gamesplay","type","number")