from data.config import show_messages, num_users, add_admin, main_menu, back_to_admin, admin_message, user_message
from aiogram import types

btn1 = [
    [
        types.KeyboardButton(text=show_messages),
        types.KeyboardButton(text=num_users)
    ],
    [
        types.KeyboardButton(text=main_menu)
    ]
]
admin_markup = types.ReplyKeyboardMarkup(keyboard=btn1, resize_keyboard=True)

btn2 = [
    [
        types.KeyboardButton(text=back_to_admin)
    ]
]
messages_markup = types.ReplyKeyboardMarkup(keyboard=btn2, resize_keyboard=True)

btn3 = [
    [
        types.KeyboardButton(text=admin_message), types.KeyboardButton(text=user_message)
    ]
]
choose_markup = types.ReplyKeyboardMarkup(keyboard=btn3, resize_keyboard=True)