
# Beauty City

В данном проекте реализован Телеграмм бот для записи в салоны красоты Beauty City
В качестве ORM системы и админки используется Django

### Как установить

Python3 должен быть установлен версии ~3.11.9. 
Используйте `pip` для установки зависимостей:
```
pip install -r requirements.txt
```
Для реализации проекта вам понадобится Telegram бот. Создать можно через [@BotFather](https://t.me/BotFather). 

Бот токен выглядит так: `1234567890:XXXxx0Xxx-xxxX0xXXxXxx0X0XX0XXXXxXx`.  

Для корректной работы потребуется файл .env  
Пример:
```
BOT_TOKEN = '' # токен, полученный от BotFather
DJANGO_SECRET_KEY = '' # заданный Вами секретный ключ
DJANGO_DEBUG = True # Включение / Выключение дебаг режима
ALLOWED_HOSTS = '["127.0.0.1", ".fvds.ru", "78.20.200.143"]' # допустимые адреса для хоста 
CROSS_OR = '["http://*.fvds.ru", "http://*.78.20.200.143"]' # допустимые переходы с адресов 
```

Потребуется выполнить первую миграцию

`python3 backend/manage.py migrate`

Также, для взаимодействия с админ-панелью необходимо создать суперпользователя:

`python3 backend/manage.py createsuperuser`

Заполнить базу данных для проверки можно также, воспользовавшись скриптом по пути extra_scripts/db_fake_data_fill.py

Его содержимое необходимо перенести в командную строку после её запуска по команде

`python3 backend/manage.py shell`

### Команды запуска

Команда для запуска бота
```
python3 backend/manage.py runbot
```

Команда для запуска сервера  
Локальный запуск
```
python3 backend/manage.py runserver
```
Для деплоя проекта рекомендуем ознакомиться с [данной](https://docs.djangoproject.com/en/5.0/howto/deployment/) статьей.

### Примеры работы

Пример корректной работы админки:

![image](https://github.com/user-attachments/assets/caadada5-6653-485e-a93d-5badd5468d4a)

Пример работы бота:

![example](https://github.com/user-attachments/assets/a97802c8-f1f1-46ad-b0ec-66bceb0a8916)


### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
