from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
# from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from keyboards.default import main_menu_user_keyboard



from utils.db_api import db

from data import config
import aiogram.utils.markdown as md

from loader import dp

# TODO: написать скрипт игры