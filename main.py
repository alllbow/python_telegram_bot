"""
Файл для запуска бота и создания БД, в случае её отсутствия
"""


from loader import dp, logger
from aiogram.utils import executor
from handlers import start_help, lowprice_highprice, history, bestdeal, echo


start_help.register_start_handlers(dp)
lowprice_highprice.register_lowprice_handlers(dp)
bestdeal.register_bestdeal_handlers(dp)
history.register_history_handlers(dp)
echo.register_echo_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    logger.info('bot start working')
