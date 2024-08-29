from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Begin session")]], resize_keyboard=True
)


cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Cancel")]], resize_keyboard=True
)


ready_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Ready", callback_data="ready")]]
)
