from aiogram import types
from aiogram import Router, F
from data import config
from data.config import main_menu
from keyboards.keyboard import back_to_main, back_markup
from keyboards.inline import confirm_user, confirm_admin
from states import user_states
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from loader import db
import datetime


from states.user_states import send_message

user_router = Router()

@user_router.message(F.text == config.send_to_admin)
async def send_admin(message: types.Message, state: FSMContext):
    await state.set_state(user_states.send_message.content)
    markup = None
    if not config.IsAdmin(message):
        markup = back_to_main
    elif not config.AdminMode:
        markup = back_markup
    await message.answer(text="Please, send your message 👇", reply_markup=markup)

@user_router.message(user_states.send_message.content)
async def get_content(message: types.Message, state: FSMContext):
    await state.set_state(user_states.send_message.confirm)
    markup = None
    if not config.IsAdmin(message):
        markup = confirm_user
    else:
        markup = confirm_admin
    await message.reply("Can you confirm your actions?", reply_markup=markup)

@user_router.message(user_states.send_message.confirm)
async def message_already(message: types.Message, state: FSMContext):
    await message.answer("<b>You already have another message pending...</b>\nPlease, confirm your action or cancel it to send another message!")


@user_router.callback_query(user_states.send_message.confirm)
async def user_confirming_message(query: types.CallbackQuery, state: FSMContext):
    # print(query.data)
    markup = None
    if not config.IsAdmin(query.message.reply_to_message):
        markup = back_to_main
    elif not config.AdminMode:
        markup = back_markup
    if query.data == "user_confirm":
        currentDateTime = datetime.datetime.now()
        currentDateTimestr = currentDateTime.strftime("%d.%m.%Y %H:%M:%S")
        await query.answer(text="Message sent!")
        await query.bot.send_message(config.ADMIN, text="New message received!")
        msg = await query.bot.forward_message(config.CHANNEL_ID, query.message.chat.id, query.message.reply_to_message.message_id, protect_content=False)
        user_id = db.fetchone("SELECT idx FROM users WHERE tgid = ?", (query.from_user.id,))[0]
        db.query("INSERT INTO messages(from_user_id, sent_date, msg_id, replied) VALUES (?, ?, ?, ?)", (user_id, currentDateTimestr, msg.message_id, 0))

        await query.message.answer("<b>Message successfully sent!</b>\nAdmin should reply in few hours...\n\nYou can send another message 👇", reply_markup=markup)
        await state.set_state(user_states.send_message.content)
        await query.message.delete()

    elif query.data == "user_cancel":
        await query.message.answer("<b>Process canceled!</b>\n\nYou can send another message 👇", reply_markup=markup)
        await state.set_state(user_states.send_message.content)
        await query.message.delete()

#
# @user_router.message(F.text == config.my_messages)
# async def send_admin(message: types.Message):
#     markup = None
#     if not config.IsAdmin(message):
#         markup = back_to_main
#     elif not config.AdminMode:
#         markup = back_markup
#     await message.answer(text="You can here see your messages", reply_markup=markup)
#def sending_question
    # text = message.text
    # if len(text) > 0:
    #     await message.bot.send_message(chat_id=config.ADMIN, text=f"Question from user <b>{message.from_user.id}</b>:\n{text}")
    #     await message.answer("Your question has been sent to the admin.")
    # else:
    #     await message.answer("Please type a message to ask the admin.")

def register_user_handlers(dp):
    dp.include_router(user_router)
