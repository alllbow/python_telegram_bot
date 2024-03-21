from asyncio.log import logger
from aiogram import Dispatcher, types
from keyboards import key_text
from keyboards.keyboards import menu_keyboard
from loader import bot
from settings import constants


async def start_command(message: types.Message) -> None:
    """
        Функция -  обрабатывает команду start
        :param message: Message
        :return: None
    """
    try:
        await bot.send_message(message.from_user.id, constants.WELCOME, reply_markup=menu_keyboard())
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
        await bot.send_message(message.from_user.id, constants.REQUEST_ERROR)


async def help_command(message: types.Message) -> None:
    """
           Функция -  обрабатывает команду help
           :param message: Message
           :return: None
           """
    try:
        await bot.send_message(message.from_user.id, constants.HELP_MESSAGE)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


# Регистрируем хендлеры
def register_start_handlers(dp: Dispatcher) -> None:
    """
        Функция - регистрирует хендлеры  файла
        :param dp: Dispatcher
        :return: None
    """
    dp.register_message_handler(start_command, commands=['start'], state=None)
    dp.register_message_handler(help_command, commands=['help'], state=None)
    dp.register_message_handler(help_command, lambda message: message.text == key_text.KEY_HELP, state=None)
