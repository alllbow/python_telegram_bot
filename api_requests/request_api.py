from datetime import datetime
from typing import List, Tuple, Optional, Dict
from requests import Response
from loader import logger
from settings.settings import QUERY_SEARCH, URL_SEARCH, HEADERS, QUERY_PROPERTY_LIST, URL_PROPERTY_LIST, QUERY_PHOTO, \
    URL_PHOTO, QUERY_BESTDEAL
import json
import requests


def request_cities(city: str) -> List[Tuple]:
    """
           Функция - обрабатывает запрос к API.
           Получает инфорацию о городах.
           :param city: str
           :return None
    """
    try:
        logger.info('request_cities')
        QUERY_SEARCH['query'] = city
        response = request_func(URL_SEARCH, HEADERS, QUERY_SEARCH)
        dict_1 = json.loads(response.text)
        lst = []
        for i in range(len(dict_1["suggestions"][0]["entities"])):
            itog = (dict_1["suggestions"][0]["entities"][i]["caption"])
            destination_id = (dict_1["suggestions"][0]["entities"][i]["destinationId"])
            itog1 = itog.replace("<span class='highlighted'>", "")
            itog2 = itog1.replace("</span>", "")
            lst.append((itog2, destination_id))
        return lst
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def request_hotels(destination_id: int, arrival_date: datetime, departurel_date: datetime, command: str,
                   currency: str) -> Dict:
    """
           Функция - обрабатывает запрос к API.
           Получает инфорацию об отелях.
           :param destination_id: int
           :param arrival_date: datetime
           :param departurel_date: datetime
           :param command: str
           :param currency: str
           :return Dict
    """
    try:
        logger.info('request_hotels')
        QUERY_PROPERTY_LIST['destinationId'] = destination_id
        QUERY_PROPERTY_LIST['checkIn'] = arrival_date
        QUERY_PROPERTY_LIST['checkOut'] = departurel_date
        if command == '/highprice':
            QUERY_PROPERTY_LIST['sortOrder'] = '-PRICE'
        QUERY_PROPERTY_LIST['currency'] = currency
        response = request_func(URL_PROPERTY_LIST, HEADERS, QUERY_PROPERTY_LIST)
        if str(response.status_code).startswith('2'):
            dict_hotels = json.loads(response.text)['data']['body']['searchResults']['results']
            return dict_hotels
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def request_hotels_bestdeal(value_dict: Dict) -> Dict:
    """
           Функция - обрабатывает запрос к API.
           Получает инфорацию о отелях.
           :param value_dict: Dict
           :return Dict
    """
    try:
        logger.info('request_hotels_bestdeal')
        QUERY_BESTDEAL['destinationId'] = value_dict['destination_id']
        QUERY_BESTDEAL['checkIn'] = value_dict['arrival_date']
        QUERY_BESTDEAL['checkOut'] = value_dict['departurel_date']
        QUERY_BESTDEAL['currency'] = value_dict['currency']
        QUERY_BESTDEAL['range_price_min'] = value_dict['range_price_min']
        QUERY_BESTDEAL['range_price_max'] = value_dict['range_price_max']
        QUERY_BESTDEAL['range_distance_min'] = value_dict['range_distance_min']
        QUERY_BESTDEAL['range_distance_max'] = value_dict['range_distance_max']
        response = request_func(URL_PROPERTY_LIST, HEADERS, QUERY_BESTDEAL)
        if str(response.status_code).startswith('2'):
            dict_hotels = json.loads(response.text)['data']['body']['searchResults']['results']
            return dict_hotels
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def request_get_photo(hotel_id: int) -> Response:
    """
    Функция - делающая запрос на API по адресу: 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'.
    Вызывается при необходимости вывода фотографий к отелям. Возвращает Response, содержащий в себе список url
    фотографий отелей.

    :param hotel_id: int
    :return: Response
    """
    try:
        QUERY_PHOTO['id'] = hotel_id
        response = request_func(URL_PHOTO, HEADERS, QUERY_PHOTO)
        return response
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def check_status_code(response: Response) -> Optional[bool]:
    """
    Функция - проверяет статус-код ответа. Если статус-код начинается на '2', то возвращает True,
    в противном случае пишет лог об ошибке.

    :param response: Response
    :return: Optional[bool]
    """
    if requests.codes.ok == response.status_code:
        return True
    else:
        logger.error('Ошибка запроса', exc_info=response.status_code)


def request_func(url, headers, params):
    try:
        response = requests.get(url=url, headers=headers, params=params, timeout=15)
        return response
    except TimeoutError as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
