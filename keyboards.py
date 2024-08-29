from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Begin session")]], resize_keyboard=True
)
