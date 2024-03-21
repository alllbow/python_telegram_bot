from typing import Union
from aiogram import Dispatcher, types
from database.database import *
from keyboards import key_text, keyboards_text
from keyboards.keyboards import keyboard_history, menu_keyboard
from loader import bot, logger
from aiogram.types import CallbackQuery, Message, InputMediaPhoto
from settings import constants
from peewee import ModelSelect


async def history_command(message: Union[Message, CallbackQuery]) -> None:
    """
        Функция -  обрабатывает команду history
        :param message: Message
        :return: None
        """
    logger.info(str(message.text))
    await bot.send_message(message.from_user.id, constants.HISTORY_MENU_MESSAGE,
                           reply_markup=keyboard_history(message.text))


async def history_menu(call: types.CallbackQuery):
    """
           Хендлер - обрабатывает нажатие на кнопки( просмотр истории, удаление)
           :param call: CallbackQuery
           :return None
    """
    logger.info(str(call.message.text))
    if call.data == keyboards_text.HISTORY_LIST[0]:
        await bot.send_message(call.from_user.id, constants.HISTORY_MENU_MESSAGE,
                               reply_markup=keyboard_history(call.message.text))
    else:
        users = Users.select().where(Users.user_id == call.from_user.id)
        for user in users:
            Hotels.delete().where(Hotels.command_id_id == user).execute()
            print(user)
            Users.delete().where(Users.id == user).execute()
        await bot.send_message(call.from_user.id, constants.HISTORY_DELETE)
        await bot.send_message(call.from_user.id, constants.HELP_MESSAGE, reply_markup=menu_keyboard())


async def history_menu_show(call: types.CallbackQuery):
    """
           Хендлер - обрабатывает нажатие на кнопки варианта просмотра истории
           :param call: CallbackQuery
           :return None
    """
    logger.info(str(call.message.text))
    if call.data == keyboards_text.HISTORY_SHOW_LIST[0]:
        users = Users.select().where(Users.user_id == call.from_user.id)
    else:
        users = Users.select().where(Users.user_id == call.from_user.id).order_by(Users.created_at.desc()).limit(5)
    await history_logic(call, users)


async def history_logic(call: types.CallbackQuery, users: ModelSelect):
    """
           Хендлер - обрабатывает нажатие на кнопки варианта просмотра истории
           :param call: CallbackQuery
           :param users: ModelSelect
           :return None
    """
    logger.info(str(call.message.text))
    if len(users) > 0:
        for user in users:
            text = constants.HISTORY_COMMAND_RU.format(user.created_at, user.command, user.city, user.date_in,
                                                       user.date_out)
            await bot.send_message(call.from_user.id, text, parse_mode='Markdown')
            hotels = Hotels.select().where(Hotels.command_id_id == user)
            if len(hotels) > 0:
                for hotel in hotels:
                    if hotel.photo:
                        media_list = []
                        for elem, photo in enumerate(hotel.photo.split()):
                            media_list.append(InputMediaPhoto(photo, caption=hotel.hotel_info if elem == 0 else '',
                                                              parse_mode='Markdown'))
                        await bot.send_media_group(call.from_user.id, media_list)
                    else:
                        await bot.send_message(call.from_user.id, hotel.hotel_info, parse_mode='Markdown')

            else:
                await bot.send_message(call.from_user.id, constants.HISTORY_EMPTY_HOTELS)
    else:
        await bot.send_message(call.from_user.id, constants.HISTORY_EMPTY)


def register_history_handlers(dp: Dispatcher):
    """
        Функция - регистрирует хендлеры  файла
        :param dp: Dispatcher
        :return: None
    """
    dp.register_message_handler(history_command, commands='history')
    dp.register_message_handler(history_command, lambda message: message.text in key_text.KEY_HISTORY, state=None)
    dp.register_callback_query_handler(history_menu, lambda call: call.data in key_text.HISTORY_LIST, state=None)
    dp.register_callback_query_handler(history_menu_show, lambda call: call.data in key_text.HISTORY_SHOW_LIST,
                                       state=None)
