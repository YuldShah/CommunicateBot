from aiogram import types
from data.config import cancel, confirm

btn4 = [
    [
        types.InlineKeyboardButton(text=cancel, callback_data="user_cancel"),
        types.InlineKeyboardButton(text=confirm, callback_data="user_confirm"),
    ]
]
confirm_user = types.InlineKeyboardMarkup(inline_keyboard=btn4)

btn5 = [
    [
        types.InlineKeyboardButton(text=cancel, callback_data="user_cancel"),
        types.InlineKeyboardButton(text=confirm, callback_data="user_confirm"),
    ]
]
confirm_admin = types.InlineKeyboardMarkup(inline_keyboard=btn5)