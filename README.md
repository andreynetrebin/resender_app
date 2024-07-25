
# Resender

Flask приложение для формирования сообщений (XML, JSON) из различных источников данных с последующей отправкой их в брокер сообщений IBM MQ.

## Tech Stack

Flask, Bootstrap, jQuery
## Features

- Интуитивно понятный интерфейс
- Админская панель
- REST API для получения результатов выполнения запросов к БД
- Swagger документация к REST API

## Flask Application Structure
```
.
├── .
├── │   .env                        
├── │   app.db                      # база данных приложения  
├── │   config.py                   # конфигурация приложения
├── │   requirements.txt            # зависимости
├── │
├── ├───app
├── │   │   __init__.py             # создание приложения
├── │   │   db.py                   # инициализация базы данных
├── │   │   dict_config.py          # конфигурация логирования
├── │   │   users.py                # модель пользователей
├── │   │
├── │   ├───admin                   # модуль Админ-панели
├── │   │   │   admin.py                # views модуля
├── │   │   │
├── │   │   ├───static                  # Javascripts/CSS файлы модуля
├── │   │   │
├── │   │   ├───templates               # html-шаблоны модуля  
├── │   │
├── │   ├───api                     # модуль API   
├── │   │   │   api.py                  # views модуля  
├── │   │   │
├── │   │   ├───static                  # Javascripts/CSS файлы модуля (OpenAPI Specification)
├── │   │   │
├── │   │   ├───templates               # html-шаблоны модуля (OpenAPI Specification)
├── │   │
├── │   ├───auth                    # модуль авторизации/аутентификации
├── │   │   │   auth.py                 # views модуля
├── │   │
├── │   ├───database
├── │   │   │   init_db.py          # скрипт по инициалиции БД  
├── │   │   │   migrate.py          # скрипт по обновлению БД
├── │   │
├── │   ├───main                    # модуль стартовой страницы
├── │   │   │   main.py                 # views модуля
├── │   │   │
├── │   │   ├───static                  # Javascripts/CSS файлы модуля + auth модуля
├── │   │   │
├── │   │   ├───templates               # html-шаблоны модуля + auth модуля
├── │   │
├── │   ├───profile                 # модуль профилей пользователей
├── │   │   │   profile.py              # views модуля
├── │   │   │
├── │   │   ├───static              # Javascripts/CSS файлы модуля
├── │   │   │
├── │   │   ├───templates           # html-шаблоны модуля
├── │   │   │
├── │   │
├── │   ├───resend                  # модуль основного функционала
├── │   │   │   utils.py                # вспомогательные скрипты
├── │   │   │   resend.py               # views модуля
├── │   │   │
├── │   │   ├───prepare_data            # каталог со скриптами предварительной обработки данных
├── │   │   │
├── │   │   ├───static                  # Javascripts/CSS файлы модуля             
├── │   │   │
├── │   │   ├───templates               # html-шаблоны модуля
├── │   │
├── │
├── ├───tests
├── │   └───__init__.py
├── │           test_basic.py        # тесты
└── │
```

## Database Structure

![diagram_db](https://github.com/user-attachments/assets/1b065ab0-ebce-4d52-a9c0-364802ad1301)

## Screenshots
-стартовая страница

![start_page](https://github.com/user-attachments/assets/560ec36c-4136-48a4-a413-1a57b3cd9a78)

-форма входа

![login_page](https://github.com/user-attachments/assets/444737c4-bdcf-4956-8c5f-ec4800675080)

-основное меню

![resend_works_page](https://github.com/user-attachments/assets/68984976-4f0b-4ee5-8800-2db543df7848)

-админ-панель

![admin_page](https://github.com/user-attachments/assets/21c68f88-193b-499a-a17b-92dd6c7b0307)

-страница Swagger-документации к API

![api_doc_page](https://github.com/user-attachments/assets/20418d5f-704b-4a5c-8c24-45c6a1c001b1)


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`FLASK_APP`

`SECRET_KEY`


## Installation

Install with pip:

```bash
$ pip install -r requirements.txt
```
    
## Run Locally

Clone the project

```bash
  git clone [https://link-to-project](https://github.com/andreynetrebin/resender_app.git)
```

Go to the project directory

```bash
  cd my-project
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Init database

```bash
  flask init-db
```

Start the server

```bash
  flask run
```


## Running Tests

To run tests, run the following command

```bash
  python tests\test_basic.py
```
## Acknowledgements

 - [Flask configuration of logging](https://flask.palletsprojects.com/en/3.0.x/logging/#basic-configuration)
 - [How to add authentication to your app with flask-login](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login)
 - [Enhance Your Flask Web Project With a Database](https://realpython.com/flask-database/)
 - [Flask для начинающих — Часть 2 пишем landing page+admin panel](https://habr.com/ru/articles/784770/)
 - [Проектирование RESTful API с помощью Python и Flask](https://habr.com/ru/articles/246699/)
 - [How to structure a large flask application with flask blueprints](https://www.digitalocean.com/community/tutorials/how-to-structure-a-large-flask-application-with-flask-blueprints-and-flask-sqlalchemy)

## Roadmap

- Добавить документацию

- Расширить функционал админки

- Увеличить покрытие тестами

