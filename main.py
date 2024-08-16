import logging
import sys
from loader import dp, db, bot, import_users
from aiogram import types
import asyncio
from data import config
from aiogram.filters import CommandStart
from aiogram import F
from handlers.admin import register_admin_handlers
from handlers.user import register_user_handlers, register_messages_handlers
from keyboards.keyboard import admin_markup, user_markup, back_to_main, choose_markup, user_markup_admin
from datetime import datetime
# from states import admin_states
from aiogram.fsm.context import FSMContext

@dp.message(CommandStart())
@dp.message(F.text == config.main_menu)
async def process_command(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    response = f"Welcome, <b>{message.from_user.first_name}</b> to the Main menu!\n"
    markup = user_markup
    # print(config.USERS)
    if str(message.from_user.id) not in config.USERS:
        reg_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        db.query("INSERT INTO users(tgid, full_name, username, reg_date) VALUES (?, ?, ?, ?)", (message.from_user.id, message.from_user.full_name, message.from_user.username, reg_date))
        response = f"Hello, <b>{message.from_user.first_name}</b>!\nWelcome to the bot!"
        config.USERS.append(str(message.from_user.id))
    if message.from_user.id == config.ADMIN:
        markup = choose_markup
    await message.answer(text=response, reply_markup=markup)

@dp.message(F.text == config.user_message)
@dp.message(F.text == config.back_to_user)
async def user_mode(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id == config.ADMIN:
        await state.clear()
        config.AdminMode = False
        await message.answer('User mode on.', reply_markup=user_markup_admin)

@dp.message(F.text == config.admin_message)
@dp.message(F.text == config.back_to_admin)
async def admin_mode(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id == config.ADMIN:
        await state.clear()
        config.AdminMode = True
        await message.answer('Admin mode on.', reply_markup=admin_markup)

async def on_startup():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    db.create_tables()
    import_users()
    logging.warning("Database started...")

async def on_shutdown():
    logging.warning("Shutting down..")
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bot down")

async def main():
    await on_startup()
    register_admin_handlers(dp)
    register_user_handlers(dp)
    register_messages_handlers(dp)
    await dp.start_polling(bot)
    await on_shutdown()



if __name__ == '__main__':
    asyncio.run(main())