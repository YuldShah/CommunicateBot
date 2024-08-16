from data.config import send_to_admin, my_messages, main_menu, back_to_user, cancel, confirm
from aiogram import types

btn1 = [
    [
        types.KeyboardButton(text=send_to_admin),
        types.KeyboardButton(text=my_messages)
    ]
]
user_markup = types.ReplyKeyboardMarkup(keyboard=btn1, resize_keyboard=True)

btn1_adm = [
    [
        types.KeyboardButton(text=send_to_admin),
        types.KeyboardButton(text=my_messages)
    ],
    [
        types.KeyboardButton(text=main_menu)
    ]
]
user_markup_admin = types.ReplyKeyboardMarkup(keyboard=btn1_adm, resize_keyboard=True)



btn2 = [
    [
        types.KeyboardButton(text=main_menu),
    ]
]
back_to_main = types.ReplyKeyboardMarkup(keyboard=btn2, resize_keyboard=True)

btn3 = [
    [
        types.KeyboardButton(text=back_to_user)
    ]
]

back_markup = types.ReplyKeyboardMarkup(keyboard=btn3, resize_keyboard=True)