"""
Файл для создания экземпляров: бота и логгера.
Так же содержит декоратор для отлова исключений и логгирования ошибок
"""
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from logging_config import custom_logger
from settings.settings import TOKEN


logger = custom_logger('bot_logger')
storage = MemoryStorage()
bot = Bot(token=TOKEN)

dp = Dispatcher(bot, storage=storage)

