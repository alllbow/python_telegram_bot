from typing import List
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards import key_text, keyboards_text
from keyboards.key_text import CURRENCY_LIST, CHOICE_PHOTO
from settings import constants


def menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    first_key = KeyboardButton(text=key_text.KEY_LOWPRICE)
    second_key = KeyboardButton(text=key_text.KEY_HIGHPRICE)
    third_key = KeyboardButton(text=key_text.KEY_BESTDEAL)
    fourth_key = KeyboardButton(text=key_text.KEY_HISTORY)
    fifth_key = KeyboardButton(text=key_text.KEY_HELP)
    keyboard.add(first_key, second_key, third_key, fourth_key, fifth_key)
    return keyboard


def currency_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
    for elem in CURRENCY_LIST:
        keyboard.add(InlineKeyboardButton(text=elem, callback_data=f"{elem}"))
    return keyboard


def cities_keyboard(lst: List) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for elem in lst:
        keyboard.add(InlineKeyboardButton(text=elem[0], callback_data=f"{elem[0]}&{elem[1]}"))
    return keyboard


def photo_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for elem in CHOICE_PHOTO:
        keyboard.add(InlineKeyboardButton(text=elem, callback_data=f"{elem}"))
    return keyboard


def count_hotel_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=5)
    count_hotel_key_1 = InlineKeyboardMarkup(text=1, callback_data=1)
    count_hotel_key_2 = InlineKeyboardMarkup(text=2, callback_data=2)
    count_hotel_key_3 = InlineKeyboardMarkup(text=3, callback_data=3)
    count_hotel_key_4 = InlineKeyboardMarkup(text=4, callback_data=4)
    count_hotel_key_5 = InlineKeyboardMarkup(text=5, callback_data=5)
    count_hotel_key_6 = InlineKeyboardMarkup(text=6, callback_data=6)
    count_hotel_key_7 = InlineKeyboardMarkup(text=7, callback_data=7)
    count_hotel_key_8 = InlineKeyboardMarkup(text=8, callback_data=8)
    count_hotel_key_9 = InlineKeyboardMarkup(text=9, callback_data=9)
    count_hotel_key_10 = InlineKeyboardMarkup(text=10, callback_data=10)
    keyboard.add(count_hotel_key_1, count_hotel_key_2, count_hotel_key_3, count_hotel_key_4, count_hotel_key_5,
                 count_hotel_key_6, count_hotel_key_7, count_hotel_key_8, count_hotel_key_9, count_hotel_key_10)
    return keyboard


def keyboard_history(message: str) -> InlineKeyboardMarkup:
    keyboards = InlineKeyboardMarkup()
    if message == constants.HISTORY:
        keyboard_history_list = keyboards_text.HISTORY_LIST
    else:
        keyboard_history_list = keyboards_text.HISTORY_SHOW_LIST
    for elem in keyboard_history_list:
        keyboards.add(InlineKeyboardButton(text=elem, callback_data=elem))
    return keyboards
