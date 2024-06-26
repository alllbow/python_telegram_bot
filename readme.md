*** 
## Инструкция по эксплуатации телеграм-бота.
***

### Перечень файлов проекта и краткое описание.
***

### Файлы в корне проекта:

1. __.env.template__ - образец файла .env с описанием данных.
2. __.env__ - необходимо создать вручную и поместить Токен телеграм-бота и API-ключ (rapidapi.com).
3. __loader.py__ - создаёт экземпляры: телеграмм-бота и логгера.
4. __logging_config.py__ - задаёт конфигурацию логгеру
5. __main.py__ - запускает бота и создаёт базу данных, в случае её отсутствия
6. __readme.md__ - инструкция по эксплуатации телеграмм-бота


### Пакеты в корне проекта:
#### 1. settings:
* __init.py__ - инициализирует пакет settings и его содержимое
* __constants.py__ - содержит константы, для общей смены текста в коде
* __settings.py__ - подгружает переменные окружения, для работы бота и хранит параметры для запроса к API rapidapi.com
#### 2. keyboards:
* __init.py__ - инициализирует пакет keyboards и его содержимое
* __calendar.py__ - содержит функции по созданию календарей и их обработчики
* __keyboards.py__  - содержит все inline-клавиатуры участвующие в проекте (исключение: calendar)
* __keyboards_text.py__ - содержит константы, для общей смены текста в кнопках клавиатуры. Так же содержит списки с данными для обработчиков inline-кнопок.
* __key_text.py__ - - содержит константы, для общей смены текста в кнопках клавиатуры. Так же содержит списки с данными для обработчиков inline-кнопок.
#### 3. handlers:
* __init.py__ - инициализирует пакет handlers и его содержимое
* __start_help.py__ - содержит хэндлеры для отлова команд бота и отлова прочих сообщений (вне сценария)
* __lowprice_highprice.py__ - логика работы команд: lowprice, highprice и bestdeal
* __bestdeal.py__ - логика работы команды bestdeal (все отвлетвления из файла lowprice_highprice.py)
* __history.py__ - логика работы команды history
* __echo.py__ - логика работы команды eсho.py (в случае необработанных команд или сообщений от пользователя)
#### 4. database:
* __init.py__ - инициализирует пакет database и его содержимое
* __models.py__ - содержит модели классов: пользователь и отель. Так же содержит всю логику запросов к БД.
* __database.py__ - База данных peewee. 
#### 5. api_requests:
* __init.py__ - инициализирует пакет api_requests и его содержимое
* __request_api.py__ - содержит все эндпоинты делающие запросы к API


***
### Инструкция по эксплуатации:

Для запуска бота, Вам необходимо будет создать виртуальное окружение. Поместить токен-бота и API-ключ rapidapi.com в переменные окружения (Файл .env). Далее запускаем бота в файле main.py. Для отслеживания функционирования бота и возможных ошибок, ведётся логгирование, путём записи данных в файлы. info.log - записывает всю информацию, которая логируется в боте. error.log - записывает только возникшие исключения. Параметры логгирования можно изменить в файле logging_config.py. По умолчанию в конфигурации логгера, логи в файлах хранятся не более 24 часов.


### Команды бота:

* /start - Запуск бота
* /help — помощь по командам бота,
* /lowprice — вывод самых дешёвых отелей в городе,
* /highprice — вывод самых дорогих отелей в городе,
* /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра.
* /history — вывод истории поиска отелей
