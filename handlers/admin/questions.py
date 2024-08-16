from aiogram import types
from aiogram import Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram import F
from data import config
from keyboards.keyboard import messages_markup
from states import admin_states
from aiogram.fsm.context import FSMContext
from loader import db
admin_router = Router()
from data.config import reply, delete, ban_user, confirm, cancel, refresh, last_page, next_page, far_left, far_right




@admin_router.message(F.text == config.num_users)
async def number_of_users(message: types.Message):
    if config.IsAdmin(message):
        await message.answer(text=f"Number of users: {len(config.USERS)}", reply_markup=messages_markup)

@admin_router.message(F.text == config.show_messages)
async def show_all_msgs(message: types.Message, state: FSMContext, querying = False) -> None:
    await state.set_state(admin_states.show_msgs.messages)
    # await state.update_data(page=1)
    data = await state.get_data()
    if "page" not in data:
        await state.update_data(page=1)
        data = await state.get_data()
    if config.IsAdmin(message) or querying:
        msgs = db.fetchall("SELECT idx, from_user_id, sent_date, msg_id FROM messages WHERE replied = 0")
        if len(msgs) == 0:
            await message.answer("There are no messages sent or all messages have been replied!", reply_markup=messages_markup)
            await state.clear()
            return
        # print(msgs)
        cur_page = data["page"]
        num_msgs = len(msgs)
        # print(cur_page, num_msgs)
        for i in range((cur_page-1)*config.msgs_per_page, min(cur_page*config.msgs_per_page, num_msgs)):
            # print(msgs[i])
            btns = [
                [
                    types.InlineKeyboardButton(text=reply, callback_data=f"reply_{msgs[i][0]}"),
                    types.InlineKeyboardButton(text=delete, callback_data=f"delete_{msgs[i][0]}"),
                    types.InlineKeyboardButton(text=ban_user, callback_data=f"ban_user_{msgs[i][1]}"),
                ]
            ]
            admin_message_choices = types.InlineKeyboardMarkup(inline_keyboard=btns)
            snt = await message.bot.forward_message(message.chat.id, config.CHANNEL_ID, msgs[i][3],
                                                    protect_content=False)
            about_user = db.fetchone("SELECT * FROM users WHERE idx = ?", (msgs[i][1],))
            lnk = f"tg://user?id={about_user[1]}"
            if about_user[3] != "None":
                lnk = f"https://t.me/{about_user[3]}"
            await snt.reply(f"This message was sent on <b>{msgs[i][2]}</b> by user <a href=\"{lnk}\">{about_user[2]}</a>", reply_markup=admin_message_choices, disable_web_page_preview=True)
        btn_refresh = [
            [
                types.InlineKeyboardButton(text=far_left, callback_data="message_pages_far_left"),
                types.InlineKeyboardButton(text=last_page, callback_data="message_pages_last_page"),
                types.InlineKeyboardButton(text=refresh, callback_data="refresh_messages"),
                types.InlineKeyboardButton(text=next_page, callback_data="message_pages_next_page"),
                types.InlineKeyboardButton(text=far_right, callback_data="message_pages_far_right"),
            ]
        ]
        refresh_message_button = types.InlineKeyboardMarkup(inline_keyboard=btn_refresh)
        await message.answer(f"Messages are shown at the page {cur_page} of {(num_msgs+config.msgs_per_page-1)//config.msgs_per_page}👆", reply_markup=refresh_message_button)

@admin_router.callback_query(admin_states.show_msgs.messages)
async def answer_queries(query: types.CallbackQuery, state: FSMContext) -> None:
    if query.data.startswith("reply_"):
        msg_id = int(query.data[6:])
        await state.update_data(msg_id=msg_id)
        await state.set_state(admin_states.show_msgs.replying)
        await query.message.reply("Please, send your response to the message 👇")
        # print(msg_id)
    elif query.data.startswith("delete_"):
        msg_id = int(query.data[7:])
        await state.set_state(admin_states.show_msgs.deleting)
        btns = [
            [
                types.InlineKeyboardButton(text=cancel, callback_data=f"cancel_delete_{msg_id}"),
                types.InlineKeyboardButton(text=confirm, callback_data=f"confirm_delete_{msg_id}"),
            ]
        ]
        admin_delete_choices = types.InlineKeyboardMarkup(inline_keyboard=btns)
        await query.message.reply("Are you sure you want to delete this message?", reply_markup=admin_delete_choices)
        # print(msg_id)
    elif query.data.startswith("ban_user_"):
        user_id = int(query.data[9:])
        await state.set_state(admin_states.show_msgs.banning)
        btns = [
            [
                types.InlineKeyboardButton(text=cancel, callback_data=f"cancel_ban_{user_id}"),
                types.InlineKeyboardButton(text=confirm, callback_data=f"confirm_ban_{user_id}"),
            ]
        ]
        admin_ban_choices = types.InlineKeyboardMarkup(inline_keyboard=btns)
        await query.message.reply("Are you sure you want to ban this user?", reply_markup=admin_ban_choices)
        # print(user_id)
    elif query.data == "refresh_messages":
        await show_all_msgs(query.message, state, querying=True)
        await query.answer("Refreshed!")
        # types.InlineKeyboardButton(text=far_left, callback_data="message_pages_far_left"),
        # types.InlineKeyboardButton(text=last_page, callback_data="message_pages_last_page"),
        # types.InlineKeyboardButton(text=refresh, callback_data="refresh_messages"),
        # types.InlineKeyboardButton(text=next_page, callback_data="message_pages_next_page"),
        # types.InlineKeyboardButton(text=far_right, callback_data="message_pages_far_right"),
    elif query.data == "message_pages_last_page":
        data = await state.get_data()
        current_page = data["page"]
        if current_page == 1:
            await query.answer("No messages on the left!")
            return
        await state.update_data(page=current_page - 1)
        await show_all_msgs(query.message, state, querying=True)
        await query.answer("Last page!")
    elif query.data == "message_pages_next_page":
        num_msgs = db.fetchone("SELECT count(idx) FROM messages WHERE replied=0")[0]
        # print(num_msgs)
        data = await state.get_data()
        current_page = data["page"]
        if current_page == (num_msgs+config.msgs_per_page-1)//config.msgs_per_page:
            await query.answer("No messages on the right!")
            return
        await state.update_data(page=current_page+1)
        await show_all_msgs(query.message, state, querying=True)
        await query.answer("Next page!")
    elif query.data == "message_pages_far_right":
        num_msgs = db.fetchone("SELECT count(idx) FROM messages WHERE replied=0")[0]
        # print(num_msgs)
        data = await state.get_data()
        current_page = data["page"]
        if current_page == (num_msgs + config.msgs_per_page - 1) // config.msgs_per_page:
            await query.answer("No messages on the right!")
            return
        await state.update_data(page=min(current_page+config.far_skip, (num_msgs + config.msgs_per_page - 1) // config.msgs_per_page))
        await show_all_msgs(query.message, state, querying=True)
        await query.answer("Far right!")


    elif query.data == "message_pages_far_left":
        data = await state.get_data()
        current_page = data["page"]
        if current_page == 1:
            await query.answer("No messages on the left!")
            return
        await state.update_data(page=max(current_page-config.far_skip, 1))
        await show_all_msgs(query.message, state, querying=True)
        await query.answer("Far left!")

@admin_router.callback_query(admin_states.show_msgs.deleting)
async def delete_msg(query: types.CallbackQuery, state: FSMContext) -> None:
    if query.data.startswith("confirm_delete_"):
        msg_id = int(query.data[15:])
        db.query("UPDATE messages SET replied = 1 WHERE idx = ?", (msg_id,))
        await query.answer("Message deleted!")
        await query.message.answer("Message deleted!")
        await query.message.reply_to_message.delete()
        # await query.message.reply_to_message.delete()
        await query.message.delete()
        await state.set_state(admin_states.show_msgs.messages)
    elif query.data.startswith("cancel_delete_"):
        await query.answer("Deletion canceled!")
        await query.message.delete()
        await state.set_state(admin_states.show_msgs.messages)
    else:
        await query.answer("Looks like you have touched something you weren't supposed to!")

@admin_router.callback_query(admin_states.show_msgs.banning)
async def delete_msg(query: types.CallbackQuery, state: FSMContext) -> None:
    if query.data.startswith("confirm_ban_"):
        #add your banning code
        #need to first change the database structure
        msg_id = int(query.data[12:])
        db.query("UPDATE messages SET replied = 1 WHERE idx = ?", (msg_id,))
        await query.answer("User has been banned!")
        await query.message.answer("Messages deleted and user banned!")
        await query.message.reply_to_message.delete()
        # await query.message.reply_to_message.delete()
        await query.message.delete()
        await state.set_state(admin_states.show_msgs.messages)
    elif query.data.startswith("cancel_ban_"):
        await query.answer("Banning canceled!")
        await query.message.delete()
        await state.set_state(admin_states.show_msgs.messages)
    else:
        await query.answer("Looks like you have touched something you weren't supposed to!")


# @admin_router.callback_query()
# async def nothandled(query: types.CallbackQuery) -> None:
#     if config.IsAdminQuery(query) and config.AdminMode:
#         await query.answer("Query not answered!")
#         await query.message.answer("You are probably on main menu!")

@admin_router.message(admin_states.show_msgs.replying)
async def reply_message(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    usr_id = db.fetchone("SELECT tgid FROM users WHERE idx = ?", (db.fetchone("SELECT from_user_id FROM messages WHERE idx = ?", (data["msg_id"],))[0],))[0]
    try:
        await message.bot.send_message(usr_id, f"<b>Admin replied:</b>\n\n{message.text}")
        msgs_count = db.fetchone("SELECT count(idx) FROM messages WHERE replied=0")[0]
        current_page = data["page"]
        all_pages = (msgs_count+config.msgs_per_page-1)//config.msgs_per_page
        potential_page = (msgs_count+config.msgs_per_page-2)//config.msgs_per_page
        if potential_page < all_pages:
            if current_page>1:
                await state.update_data(page=current_page-1)
        db.query("UPDATE messages SET replied = 1 WHERE idx = ?", (data["msg_id"],))

        await message.answer("Response has successfully been sent!")
        await state.set_state(admin_states.show_msgs.messages)
    except TelegramForbiddenError:
        db.query("UPDATE messages SET replied = 1 WHERE idx = ?", (data["msg_id"],))
        await message.answer("Your response hasn't been successfully sent! But it was marked as read due to error:\n<b>Bot was blocked by user!</b>")
        await state.set_state(admin_states.show_msgs.messages)

# @admin_router.callback_query()
# async def user_confirming_message(query: types.CallbackQuery, state: FSMContext):
#     print(query.data)
#     if query.data == "admin_confirm":
#         data = await state.get_data()
#         await query.answer(text="Message sent")
#         await query.bot.forward_message(config.ADMIN, query.message.chat.id, query.message.reply_to_message.message_id)

# @admin_router.message(F.text == config.add_admin)
# async def broadcast_command(message: types.Message):
#     if config.IsAdmin(message):
#         await message.answer(text=f"You can add an admin in this page", reply_markup=messages_markup)


def register_admin_handlers(dp):
    dp.include_router(admin_router)