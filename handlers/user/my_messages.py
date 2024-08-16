from aiogram import types
from aiogram import Router, F
from data import config
from data.config import main_menu, last_page, far_left, far_right, next_page, refresh
from handlers.user.sos import user_router
from keyboards.keyboard import back_to_main, back_markup
from keyboards.inline import confirm_user, confirm_admin
from states import user_states
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from loader import db

user_messages = Router()

@user_messages.message(F.text == config.my_messages)
async def my_msgs(message: types.Message, state: FSMContext, querying = False) -> None:
    await state.set_state(user_states.show_my_messages.messages)
    markup = None
    # if not config.IsAdmin(message) and querying:
    #     markup = back_to_main
    # elif not config.AdminMode or querying:
    #     markup = back_markup
    data = await state.get_data()
    if "page" not in data:
        await state.update_data(page=1)
    if "user_id" not in data:
        await state.update_data(user_id=message.from_user.id)
    if "is_admin" not in data:
        await state.update_data(is_admin=config.IsAdmin(message))
    data = await state.get_data()
    if data["is_admin"]:
        markup = back_markup
    else:
        markup = back_to_main
    # print(db.fetchone("SELECT idx FROM users WHERE tgid = ?", (message.from_user.id,))[0])
    msgs = db.fetchall("SELECT sent_date, msg_id, idx, replied FROM messages WHERE from_user_id = ? AND replied = 0", (db.fetchone("SELECT idx FROM users WHERE tgid = ?", (data["user_id"],))[0],))
    if len(msgs) == 0:
        await message.answer("You have never sent a message or all your messages have been replied!", reply_markup=markup)
        return
    # print(msgs)
    cur_page = data["page"]
    num_msgs = len(msgs)
    for i in range((cur_page-1)*config.msgs_per_page, min(cur_page*config.msgs_per_page, num_msgs)):
        snt = await message.bot.forward_message(message.chat.id, config.CHANNEL_ID, msgs[i][1], protect_content=False)
        await snt.reply(f"You sent this message on <b>{msgs[i][0]}</b>", reply_markup=markup)
    btn_refresh = [
        [
            types.InlineKeyboardButton(text=far_left, callback_data="my_message_pages_far_left"),
            types.InlineKeyboardButton(text=last_page, callback_data="my_message_pages_last_page"),
            types.InlineKeyboardButton(text=refresh, callback_data="refresh_my_messages"),
            types.InlineKeyboardButton(text=next_page, callback_data="my_message_pages_next_page"),
            types.InlineKeyboardButton(text=far_right, callback_data="my_message_pages_far_right"),
        ]
    ]
    refresh_message_button = types.InlineKeyboardMarkup(inline_keyboard=btn_refresh)
    await message.answer(f"Messages are shown at the page {cur_page} of {(num_msgs+config.msgs_per_page-1)//config.msgs_per_page}👆", reply_markup=refresh_message_button)

@user_router.callback_query(user_states.show_my_messages.messages)
async def respond_query(query: types.CallbackQuery, state: FSMContext) -> None:
    if query.data == "refresh_my_messages":
        await my_msgs(query.message, state, querying=True)
        await query.answer("Refreshed!")
    elif query.data == "my_message_pages_last_page":
        data = await state.get_data()
        current_page = data["page"]
        if current_page == 1:
            await query.answer("No messages on the left!")
            return
        await state.update_data(page=current_page - 1)
        await my_msgs(query.message, state, querying=True)
        await query.answer("Last page!")
    elif query.data == "my_message_pages_next_page":
        # print(num_msgs)
        data = await state.get_data()
        current_page = data["page"]
        num_msgs = db.fetchone("SELECT count(idx) FROM messages WHERE replied=0 AND from_user_id = ?", (db.fetchone("SELECT idx FROM users WHERE tgid = ?", (data["user_id"],))[0],))[0]
        if current_page == (num_msgs + config.msgs_per_page - 1) // config.msgs_per_page:
            await query.answer("No messages on the right!")
            return
        await state.update_data(page=current_page + 1)
        await my_msgs(query.message, state, querying=True)
        await query.answer("Next page!")
    elif query.data == "my_message_pages_far_right":
        # print(num_msgs)
        data = await state.get_data()
        current_page = data["page"]
        num_msgs = db.fetchone("SELECT count(idx) FROM messages WHERE replied=0 AND from_user_id = ?", (db.fetchone("SELECT idx FROM users WHERE tgid = ?", (data["user_id"],))[0],))[0]
        # print(num_msgs)
        if current_page == (num_msgs + config.msgs_per_page - 1) // config.msgs_per_page:
            await query.answer("No messages on the right!")
            return
        await state.update_data(
            page=min(current_page + config.far_skip, (num_msgs + config.msgs_per_page - 1) // config.msgs_per_page))
        await my_msgs(query.message, state, querying=True)
        await query.answer("Far right!")


    elif query.data == "my_message_pages_far_left":
        data = await state.get_data()
        current_page = data["page"]
        if current_page == 1:
            await query.answer("No messages on the left!")
            return
        await state.update_data(page=max(current_page - config.far_skip, 1))
        await my_msgs(query.message, state, querying=True)
        await query.answer("Far left!")


def register_messages_handlers(dp):
    dp.include_router(user_messages)