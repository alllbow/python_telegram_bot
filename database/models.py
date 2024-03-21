from aiogram.dispatcher.filters.state import StatesGroup, State
from telegram_bot_calendar import DetailedTelegramCalendar


class FSMCommands(StatesGroup):
    city = State()
    city_correction = State()
    currency = State()
    range_price_min = State()
    range_price_max = State()
    range_distance_min = State()
    range_distance_max = State()
    first_day = State()
    first_month = State()
    first_year = State()
    second_day = State()
    second_month = State()
    second_year = State()
    count_hotel = State()
    photo = State()
    quantities_photo = State()


class CustomCalendar(DetailedTelegramCalendar):
    empty_year_button = ''
    empty_month_button = ''
    empty_day_button = ''
