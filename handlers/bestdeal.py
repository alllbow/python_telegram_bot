import re
from datetime import date, timedelta
from typing import List, Dict, Union
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
import settings
from api_requests.request_api import request_hotels_bestdeal
from database.models import FSMCommands, CustomCalendar
from keyboards.key_text import LSTEP
from loader import bot, logger
from settings import constants


async def min_price_state(message: types.Message, state: FSMContext) -> None:
    """
           Хендлер - обрабатывает состояние FSMCommands.range_price_min
           Запрашивает у пользователя минимальную цену за отель.
           :param message: Message
           :param state: FSMContext
           :return None
    """
    try:
        logger.info(str(message.text))
        if message.text.isdigit():
            async with state.proxy() as data:
                data['range_price_min'] = message.text
                await bot.send_message(message.from_user.id, constants.RESULT_MIN_PRICE.format(data['range_price_min']))
                await bot.send_message(message.from_user.id, constants.MAX_PRICE)
                await FSMCommands.next()
        else:
            await bot.send_message(message.from_user.id, constants.INCORRECT_PRICE)
            await bot.send_message(message.from_user.id, constants.MIN_PRICE)
        await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def max_price_state(message: types.Message, state: FSMContext) -> None:
    """
           Хендлер - обрабатывает состояние FSMCommands.range_price_max
           Запрашивает у пользователя максимальную цену за отель.
           :param message: Message
           :param state: FSMContext
           :return None
    """
    try:
        logger.info(str(message.text))
        if message.text.isdigit():
            async with state.proxy() as data:
                data['range_price_max'] = message.text
                if int(data['range_price_max']) > int(data['range_price_min']):
                    await bot.send_message(message.from_user.id,
                                           constants.RESULT_MAX_PRICE.format(data['range_price_max']))
                    await bot.send_message(message.from_user.id, constants.DISTANCE_RANGE)
                    await bot.send_message(message.from_user.id, constants.MIN_DISTANCE)
                    await FSMCommands.next()
                else:
                    await bot.send_message(message.from_user.id, constants.INCORRECT_VALUE_PRICE)
                    await bot.send_message(message.from_user.id, constants.MAX_PRICE)
        else:
            await bot.send_message(message.from_user.id, constants.INCORRECT_PRICE)
            await bot.send_message(message.from_user.id, constants.MAX_PRICE)
        await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def range_distance_min_state(message: types.Message, state: FSMContext) -> None:
    """
           Хендлер - обрабатывает состояние FSMCommands.range_distance_min
           Запрашивает у пользователя минимальную дистаницую от центра города.
           :param message: Message
           :param state: FSMContext
           :return None
    """
    try:
        logger.info(str(message.text))
        float_pattern = r'\b\d+[.,]\d+\b'
        async with state.proxy() as data:
            if [message.text] == re.findall(float_pattern, message.text) or message.text.isdigit():
                if ',' in message.text:
                    dist = re.sub(r'[,]', '.', message.text)
                else:
                    dist = message.text
                data['range_distance_min'] = dist
                await bot.send_message(message.from_user.id,
                                       constants.RESULT_MIN_DISTANCE.format(data['range_distance_min']))
                await bot.send_message(message.from_user.id, constants.MAX_DISTANCE)
                await FSMCommands.next()
            else:
                await bot.send_message(message.from_user.id, constants.INCORRECT_PRICE)
                await bot.send_message(message.from_user.id, constants.MIN_DISTANCE)
        await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


async def range_distance_max_state(message: types.Message, state: FSMContext) -> None:
    """
           Хендлер - обрабатывает состояние FSMCommands.range_distance_max
           Запрашивает у пользователя максимальную дистаницую от центра города.
           :param message: Message
           :param state: FSMContext
           :return None
    """
    try:
        logger.info(str(message.text))
        float_pattern = r'\b\d+[.,]\d+\b'
        async with state.proxy() as data:
            if [message.text] == re.findall(float_pattern, message.text) or message.text.isdigit():
                if ',' in message.text:
                    dist = re.sub(r'[,]', '.', message.text)
                else:
                    dist = message.text
                if dist > data['range_distance_min']:
                    data['range_distance_max'] = dist
                    await bot.send_message(message.from_user.id,
                                           constants.RESULT_MAX_DISTANCE.format(data['range_distance_max']))
                    calendar, step = CustomCalendar(locale='ru', min_date=date.today(),
                                                    max_date=date.today() + timedelta(days=180)).build()
                    await bot.send_message(message.from_user.id, f"Выберите {LSTEP[step]}",
                                           reply_markup=calendar)
                    await FSMCommands.next()
                else:
                    await bot.send_message(message.from_user.id, constants.INCORRECT_VALUE_DISTANCE)
                    await bot.send_message(message.from_user.id, constants.MAX_DISTANCE)
            else:
                await bot.send_message(message.from_user.id, constants.INCORRECT_DISTANCE)
                await bot.send_message(message.from_user.id, constants.MAX_DISTANCE)
        await message.delete()
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def bestdeal_logic(value_dict: Dict, results, result: List) -> Union[List[Dict], bool]:
    """
    Функция - обрабатывающая десериализованный ответ с API. Проходит циклом по отелям и подбирает
    отель с подходящей удаленностью от центра. В случае, если не набралось необходимое количество отелей
    (Пользовательский выбор + 5 отелей запасных, в случае возникновения ошибок), то обращаемся к функции
    bestdeal_additional_request, для повторного запроса на следующей странице. Чтобы пользователь долго не ожидал
    инофрмацию, к API делается ещё два дополнительных запроса по отелям, если они не набирается необходимое
    количество отелей, то пользователь получает сообщение, что отели не найдены.
    :param value_dict: Dict
    :param results: List[Dict]
    :param result: List
    :return: Union [List[Dict], bool]
    """
    try:
        for hotel in results:
            distance = re.sub(r'[\D+]', '', hotel['landmarks'][0]['distance'])
            if int(value_dict['range_distance_min']) <= int(distance) <= int(value_dict['range_distance_max']):
                result.append(hotel)
        if len(result) < int(value_dict['count_hotel']) + 5:
            settings.settings.QUERY_BESTDEAL['pageNumber'] = int(settings.settings.QUERY_BESTDEAL['pageNumber']) + 1
            if settings.settings.QUERY_BESTDEAL['pageNumber'] == 4:
                return False
            else:
                bestdeal_additional_request(value_dict, result)
        elif len(result) >= int(value_dict['count_hotel']) + 5:
            settings.settings.QUERY_BESTDEAL['pageNumber'] = 1
            return result
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def bestdeal_additional_request(value_dict: Dict, result: List[Dict]) -> None:
    """
    Функция - обращается к файлу request_api, функции request_bestdeal.
    Полученный ответ от API, отправляет в bestdeal_logic

    :param value_dict: Dict
    :param result: List[Dict]
    :return: None
    """
    try:
        result_hotels = request_hotels_bestdeal(value_dict)
        bestdeal_logic(value_dict, result_hotels, result)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_bestdeal_handlers(dp: Dispatcher) -> None:
    """
        Функция - регистрирует хендлеры  файла
        :param dp: Dispatcher
        :return: None
    """
    dp.register_message_handler(min_price_state, state=FSMCommands.range_price_min)
    dp.register_message_handler(max_price_state, state=FSMCommands.range_price_max)
    dp.register_message_handler(range_distance_min_state, state=FSMCommands.range_distance_min)
    dp.register_message_handler(range_distance_max_state, state=FSMCommands.range_distance_max)
