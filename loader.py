from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from data import config
from utils.db import DatabaseManager

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
db = DatabaseManager("data/database.db")

def import_users():
    already_users = db.fetchall("SELECT tgid FROM users")
    config.USERS += [item for tup in already_users for item in tup]