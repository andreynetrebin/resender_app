
# Resender

Flask приложение для формирования сообщений (xml, json) из различных источников и их отправке в брокер сообщений IBM MQ.

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
├── │   app.db
├── │   config.py
├── │   README.md
├── │   requirements.txt
├── │   test_app.db
├── │
├── ├───app
├── │   │   db.py
├── │   │   dict_config.py
├── │   │   ext_database.py
├── │   │   users.py
├── │   │   __init__.py
├── │   │
├── │   ├───admin
├── │   │   │   admin.py
├── │   │   │
├── │   │   ├───static
├── │   │   │   ├───css
├── │   │   │   └───js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───admin
├── │   │
├── │   ├───api
├── │   │   │   api.py
├── │   │   │
├── │   │   ├───downloads
├── │   │   │
├── │   │   ├───static
├── │   │   │   │   openapi.json
├── │   │   │   ├───css
├── │   │   │   ├───img
├── │   │   │   └───js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───api
├── │   │   │
├── │   │
├── │   ├───auth
├── │   │   │   auth.py
├── │   │   │
├── │   │
├── │   ├───database
├── │   │   │   init_db.py
├── │   │   │   schema.sql
├── │   │   │   __init__.py
├── │   │   │
├── │   │
├── │   ├───ext_databases
├── │   │   │   db_queries.py
├── │   │   │
├── │   │
├── │   ├───main
├── │   │   │   main.py
├── │   │   │
├── │   │   ├───static
├── │   │   │   ├───css
├── │   │   │   │
├── │   │   │   └───js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───main
├── │   │
├── │   ├───profile
├── │   │   │   profile.py
├── │   │   │
├── │   │   ├───static
├── │   │   │   ├───css
├── │   │   │   │
├── │   │   │   └───js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───profile
├── │   │   │
├── │   │
├── │   ├───resend
├── │   │   │   files_data_handler.py
├── │   │   │   mq.py
├── │   │   │   resend.py
├── │   │   │   settings.ini
├── │   │   │
├── │   │   ├───prepare_data
├── │   │   │
├── │   │   ├───static
├── │   │   │   ├───css
├── │   │   │   │
├── │   │   │   └───js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───resend
├── │   │
├── │
├── ├───tests
├── │   └───__init__.py
├── │           test_basic.py
└── │
```

## Database Structure

![alt text](https://github.com/andreynetrebin/resender_app/images/main/diagram_db.png?raw=true)

## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)

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
  git clone https://link-to-project
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

