import json
import re
from datetime import date, timedelta, datetime
import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputMediaPhoto
from api_requests.request_api import request_cities, request_hotels, request_get_photo, request_hotels_bestdeal
from database.models import FSMCommands, CustomCalendar
from handlers.bestdeal import bestdeal_logic
from keyboards import key_text
from keyboards.key_text import LSTEP
from keyboards.keyboards import currency_keyboard, cities_keyboard, photo_keyboard, count_hotel_keyboard
from loader import bot, logger
from settings import constants
from settings.settings import URL_HOTEL
from database.database import *


async def lowprice_command(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер - обрабатывает команду /lowprice
    :param message: Message
    :param state: FSMContext
    :return None
    """
    try:
        logger.info(str(message.text))
        await FSMCommands.city.set()
        async with state.proxy() as data:
            data['command'] = message.text
        await bot.send_message(message.from_user.id, constants.CITY)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def city_state(message: types.Message) -> None:
    """
        Хендлер - обрабатывает состояние FSMCommands.city
        :param message: Message
        :return None
        """
    logger.info(str(message.text))
    lst = request_cities(message.text)
    if lst:
        await bot.send_message(message.from_user.id, constants.CORRECTION, reply_markup=cities_keyboard(lst))
        await FSMCommands.next()
    else:
        await bot.send_message(message.from_user.id, constants.INCORRECT_CITY)
    await message.delete()


async def city_correction_state(call: types.CallbackQuery, state: FSMContext) -> None:
    """
           Хендлер - обрабатывает состояние FSMCommands.city_correction
           :param call: CallbackQuery
           :param state: FSMContext
           :return None
    """
    logger.info(str(call.message.text))
    city = call.data.split('&')
    async with state.proxy() as data:
        data['city'] = city[0]
        data['destination_id'] = city[1]
        await FSMCommands.next()
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=constants.CITY_RESULT.format(city[0]))
        await bot.send_message(call.from_user.id, constants.CURRENCY, reply_markup=currency_keyboard())


async def currency(call: types.CallbackQuery, state: FSMContext) -> None:
    """
           Хендлер - обрабатывает состояние FSMCommands.currency
           Проверяет введнную команду пользователя, если выбрана команда bestdeal,
           то переходит к следующему состоянию, иначе переходит на состояние  FSMCommands.first_day.
           :param call: CallbackQuery
           :param state: FSMContext
           :return None
    """
    logger.info(str(call.message.text))
    async with state.proxy() as data:
        data['currency'] = call.data
    await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                text=constants.RESULT_CURRENCY + data['currency'])
    if data['command'] == '/bestdeal' or data['command'] == key_text.KEY_BESTDEAL:
        await FSMCommands.next()
        await bot.send_message(call.from_user.id, constants.MIN_PRICE)
    else:
        await FSMCommands.first_day.set()
        calendar, step = CustomCalendar(locale='ru', min_date=date.today(),
                                        max_date=date.today() + timedelta(days=180)).build()
        await bot.send_message(call.from_user.id, f"Выберите {LSTEP[step]}",
                               reply_markup=calendar)


async def cal(call: types.CallbackQuery, state: FSMContext):
    """
           Хендлер - обрабатывает логику работы с календарем.
           Принимает дату заезда и дату выезда, на данном хендлере
           используется 6 обработчиков
           :param call: CallbackQuery
           :param state: FSMContext
           :return None
    """
    logger.info(str(call.message.text))
    async with state.proxy() as data:
        if data.get('arrival_date', None) is None:
            min_date = date.today()
            max_date = date.today() + timedelta(days=180)
        else:
            min_date = data['arrival_date'] + timedelta(days=1)
            max_date = min_date + timedelta(days=180)
        result, key, step = CustomCalendar(locale='ru', min_date=min_date, max_date=max_date).process(call.data)
        if not result and key:
            await bot.edit_message_text(
                f"Выберите {LSTEP[step]}:", call.message.chat.id, call.message.message_id, reply_markup=key
            )
        else:
            if data.get('arrival_date', None) is None:
                data['arrival_date'] = result
                calendar, step = CustomCalendar(locale='ru', min_date=min_date, max_date=max_date).build()
                await bot.send_message(call.from_user.id, constants.SHOWING_DATE_IN.format(data['arrival_date']))
                await bot.send_message(call.from_user.id, constants.DATE_OUT, reply_markup=calendar)
                await call.message.delete()
            else:
                data['departurel_date'] = result
                data['count_days'] = int((data['arrival_date'] - result).total_seconds() / (24 * 3600))
                await bot.send_message(call.from_user.id, constants.SHOWING_DATE_OUT.format(data['departurel_date']))
                await bot.send_message(call.from_user.id, constants.COUNT_HOTEL, reply_markup=count_hotel_keyboard())
                await call.message.delete()
    await FSMCommands.next()


async def count_hotel_state(call: types.CallbackQuery, state: FSMContext):
    """
           Хендлер - обрабатывает состояние FSMCommands.count_hotel
           Записывает указанное кол-во отелей пользователя
           :param call: CallbackQuery
           :param state: FSMContext
           :return None
    """
    logger.info(str(call.message.text))
    async with state.proxy() as data:
        data['count_hotel'] = call.data
    await FSMCommands.next()
    await bot.send_message(call.from_user.id, constants.RESULT_COUNT_HOTEL + data['count_hotel'])
    await bot.send_message(call.from_user.id, constants.QUESTION_PHOTO, reply_markup=photo_keyboard())
    await call.message.delete()


async def photo_state(call: types.CallbackQuery, state: FSMContext):
    """
           Хендлер - обрабатывает состояние FSMCommands.photo_state
           Спрашивет у пользвоателя нужны ли фотографии для отелей.
           В случае положительного ответа, перемещает на следующее состояние
           которое обрабатывает кол-во фоток.
           :param call: CallbackQuery
           :param state: FSMContext
           :return None
    """
    logger.info(str(call.message.text))
    async with state.proxy() as data:
        data['photo'] = call.data
    if call.data == 'Да':
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=constants.YES_QUESTION_PHOTO)
        await bot.send_message(call.from_user.id, constants.COUNT_PHOTO, reply_markup=count_hotel_keyboard())
        await FSMCommands.next()
    else:
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                    text=constants.NO_QUESTION_PHOTO)
        await bot.send_message(call.from_user.id, constants.LOAD_RESULT)
        await send_hotel(call, state)


async def quantities_photo(call: types.CallbackQuery, state: FSMContext):
    """
           Хендлер - обрабатывает состояние FSMCommands.quantities_photo
           И запускает функцию вывода отелей с фотографиями.
           :param call: CallbackQuery
           :param state: FSMContext
           :return None
    """
    logger.info(str(call.message.text))
    async with state.proxy() as data:
        data['quantities_photo'] = call.data
        await bot.send_message(call.from_user.id, constants.RESULT_COUNT_PHOTO + data['quantities_photo'])
        await bot.send_message(call.from_user.id, constants.LOAD_RESULT)
        await call.message.delete()
    await send_hotel(call, state)


async def send_hotel(call: types.CallbackQuery, state: FSMContext):
    """
           Хендлер - обрабатывает состояние FSMCommands.quantities_photo
           Исходя из выбраннйо команды пользоваетеля, выводит результат по комадне(отелей)
           По окончаию вывода происходит сохранания данных БД.
           :param call: CallbackQuery
           :param state: FSMContext
           :return None
    """
    logger.info(str(call.message.text))
    async with state.proxy() as data:
        if data['command'] == '/bestdeal':
            value_dict = data
            response = request_hotels_bestdeal(value_dict)
            results = bestdeal_logic(value_dict, response, result=[])
            Users(created_at=datetime.today(), user_id=call.from_user.id, city=data['city'], currency=data['currency'],
                  command=data['command'],
                  date_in=data['arrival_date'], date_out=data['departurel_date'],
                  min_distance=data['range_distance_min'], max_distance=data['range_distance_max'],
                  price_min=data['range_price_min'], price_max=data['range_price_max']).save()
        else:
            results = request_hotels(data['destination_id'], data['arrival_date'], data['departurel_date'],
                                     data['command'],
                                     data['currency'])
            Users(created_at=datetime.today(), user_id=call.from_user.id, city=data['city'], currency=data['currency'],
                  command=data['command'],
                  date_in=data['arrival_date'], date_out=data['departurel_date'], ).save()
        users = Users.select().where(Users.user_id == call.from_user.id).order_by(Users.id.desc()).get().id
        if results:
            index = 0

            for i in results:
                if index == int(data['count_hotel']):
                    break
                else:
                    result = template(i, abs(data['count_days']), data['currency'])
                    if result:
                        if data['photo'] == key_text.CHOICE_PHOTO[1]:
                            Hotels(user_id=call.from_user.id, hotel_info=result,
                                   command_id_id=users).save()
                            await bot.send_message(call.from_user.id, result, parse_mode='Markdown')
                        else:
                            photo_quar = data['quantities_photo']
                            media_list, photo_str = showing_hotels_with_photo(i['id'], result, photo_quar)
                            await bot.send_media_group(call.from_user.id, media=media_list)
                            Hotels(user_id=call.from_user.id, hotel_info=result, photo=photo_str,
                                   command_id_id=users).save()
                        index += 1
            await bot.send_message(call.from_user.id, constants.SEARCH_RESULT)
        else:
            await bot.send_message(call.from_user.id, constants.NOT_FOUND)
        await state.finish()


def template(i, count_days: int, currency: str):
    """
           Функуия - подставляет данные в шаблон вывода с информацией об отеле.
           Также проверяет выбранную валюту, и считает период оплаты.
           :param i: Dict
           :param count_days: int
           :param currency: str
           :return None
    """
    try:
        name = str(i['name'])
        address = str(i['address']['streetAddress'])
        distance = str(i['landmarks'][0]['distance'])
        if currency == 'USD':
            price = int(i['ratePlan']['price']['current'][1:])
            cur_sym = '$'
            price_per_period = price * count_days
        elif currency == 'EUR':
            price = int(i['ratePlan']['price']['current'][:-2])
            cur_sym = '€'
            price_per_period = price * count_days
        else:
            price = i['ratePlan']['price']['current'][:-4]
            price_ru = re.sub(r'[,]', '', price)
            price_per_period = int(price_ru) * count_days
            cur_sym = 'RUB'
        star_rating = str(i['starRating'])
        link = URL_HOTEL.format(str(i['id']))
        return constants.HOTEL_SHOW_RU.format(name, address, distance, price, cur_sym, price_per_period, cur_sym,
                                              star_rating, link)
    except KeyError:
        return None


def showing_hotels_with_photo(i, result, photo_quar):
    """
           Функуия - формирует список с медиа-данными для отрпавки медиа-группы.
           :param i: Dict
           :param result: List
           :param photo_quar: int
           :return None
    """
    response_photo = request_get_photo(i)
    result_photo = json.loads(response_photo.text)['hotelImages']
    media_list = []
    index = 0
    photo_str = ''
    for elem in result_photo:
        photo = elem['baseUrl'].format(size='y')
        if index == int(photo_quar):
            return media_list, photo_str
        else:
            if str(requests.get(photo).status_code).startswith('2'):
                index += 1
                photo_str += photo + ' '
                media_list.append(InputMediaPhoto(photo, caption=result if index == 1 else '', parse_mode='Markdown'))


def register_lowprice_handlers(dp: Dispatcher) -> None:
    """
        Функция - регистрирует хендлеры  файла.
        :param dp: Dispatcher
        :return: None
    """
    dp.register_message_handler(lowprice_command, commands=['lowprice', 'highprice', 'bestdeal'], state=None)
    dp.register_message_handler(lowprice_command,
                                lambda message: message.text in [key_text.KEY_LOWPRICE, key_text.KEY_HIGHPRICE,
                                                                 key_text.KEY_BESTDEAL], state=None)
    dp.register_message_handler(city_state, content_types=['text'], state=FSMCommands.city)
    dp.register_callback_query_handler(city_correction_state, state=FSMCommands.city_correction)
    dp.register_callback_query_handler(currency, state=FSMCommands.currency)
    dp.register_callback_query_handler(cal, state=FSMCommands.first_day)
    dp.register_callback_query_handler(cal, state=FSMCommands.first_month)
    dp.register_callback_query_handler(cal, state=FSMCommands.first_year)
    dp.register_callback_query_handler(cal, state=FSMCommands.second_day)
    dp.register_callback_query_handler(cal, state=FSMCommands.second_month)
    dp.register_callback_query_handler(cal, state=FSMCommands.second_year)
    dp.register_callback_query_handler(count_hotel_state, state=FSMCommands.count_hotel)
    dp.register_callback_query_handler(photo_state, state=FSMCommands.photo)
    dp.register_callback_query_handler(quantities_photo, state=FSMCommands.quantities_photo)
