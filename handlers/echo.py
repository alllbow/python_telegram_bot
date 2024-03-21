from aiogram import Dispatcher, types
from settings import constants
from loader import bot, logger


async def echo_handlers(message: types.Message) -> None:
    """
     Хендлер - обрабатывает все сообщения от пользователя вне сценария.
     :param message: Message
     :return: None
     """
    try:
        await bot.send_message(message.from_user.id, constants.INCORRECT)
    except Exception as error:
        logger.error('В работе бота возникло исключение', exc_info=error)


def register_echo_handlers(dp: Dispatcher) -> None:
    """
        Функция - регистрирует хендлеры  файла
        :param dp: Dispatcher
        :return: None
    """
    dp.register_message_handler(echo_handlers)
