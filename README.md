
# Resender

Flask приложение для формирования сообщений (xml, json) из различных источников и их отправке в брокер сообщений IBM MQ.


## Features

- Интуитивно понятный интерфейс
- Админская панель
- REST API для получения результатов выполнения запросов к БД
- Swagger документация к REST API

## Flask Application Structure

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
├── │   │   │   │       bootstrap.min.css
├── │   │   │   │
├── │   │   │   └───js
├── │   │   │           bootstrap.bundle.min.js
├── │   │   │           jquery-3.7.1.slim.js
├── │   │   │           popper.min.js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───admin
├── │   │   │           add_role.html
├── │   │   │           add_user.html
├── │   │   │           add_user_role.html
├── │   │   │           admin_panel.html
├── │   │   │           adm_login.html
├── │   │   │           delete_user_role.html
├── │   │   │           editland.html
├── │   │   │           edit_user.html
├── │   │   │           layout.html
├── │   │   │
├── │   │
├── │   ├───api
├── │   │   │   api.py
├── │   │   │
├── │   │   ├───downloads
├── │   │   ├───static
├── │   │   │   │   openapi.json
├── │   │   │   │
├── │   │   │   ├───css
├── │   │   │   │       index.css
├── │   │   │   │       swagger-ui.css
├── │   │   │   │
├── │   │   │   ├───img
├── │   │   │   │       favicon-16x16.png
├── │   │   │   │       favicon-32x32.png
├── │   │   │   │
├── │   │   │   └───js
├── │   │   │           swagger-initializer.js
├── │   │   │           swagger-ui-bundle.js
├── │   │   │           swagger-ui-es-bundle-core.js
├── │   │   │           swagger-ui-es-bundle.js
├── │   │   │           swagger-ui-standalone-preset.js
├── │   │   │           swagger-ui.js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───api
├── │   │   │           index.html
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
├── │   ├───logs
├── │   │       resender.log
├── │   │
├── │   ├───main
├── │   │   │   main.py
├── │   │   │
├── │   │   ├───static
├── │   │   │   ├───css
├── │   │   │   │       bulma.min.css
├── │   │   │   │
├── │   │   │   └───js
├── │   │   │           bootstrap.bundle.min.js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───main
├── │   │   │           base.html
├── │   │   │           index.html
├── │   │   │           login.html
├── │   │   │           navbar.html
├── │   │   │           profile.html
├── │   │   │           signup.html
├── │   │   │
├── │   │
├── │   ├───profile
├── │   │   │   profile.py
├── │   │   │
├── │   │   ├───static
├── │   │   │   ├───css
├── │   │   │   │       bootstrap.min.css
├── │   │   │   │
├── │   │   │   └───js
├── │   │   │           bootstrap.bundle.min.js
├── │   │   │           jquery-3.7.1.slim.js
├── │   │   │           popper.min.js
├── │   │   │
├── │   │   ├───templates
├── │   │   │   └───profile
├── │   │   │           change_password.html
├── │   │   │           layout.html
├── │   │   │           profile.html
├── │   │   │
├── │   │
├── │   ├───resend
├── │   │   │   files_data_handler.py
├── │   │   │   mq.py
├── │   │   │   resend.py
├── │   │   │   settings.ini
├── │   │   │
├── │   │   ├───cls_files
├── │   │   │       regions.csv
├── │   │   │
├── │   │   ├───downloads
├── │   │   ├───prepare_data
├── │   │   │   │   adv_adi_prepare_data.py
├── │   │   │   │   egrn_egrul_egrip_prepare_data.py
├── │   │   │   │   npf_doc_uspn.py
├── │   │   │   │   person_apply_application_request.py
├── │   │   │   │   poszn.py
├── │   │   │   │   rnpp.py
├── │   │   │   │   szi_km_to_fbdp_prepare_data.py
├── │   │   │   │   szi_sv_to_nvp_prepare_data.py
├── │   │   │   │   upp_efs.py
├── │   │   │   │   upp_is.py
├── │   │   │   │   upp_szvm.py
├── │   │   │   │   vmse_proactive.py
├── │   │   │   │   vmse_zapros.py
├── │   │   │   │
├── │   │   │
├── │   │   ├───static
├── │   │   │   ├───css
├── │   │   │   │       bootstrap.min.css
├── │   │   │   │       menu.css
├── │   │   │   │       pricing.css
├── │   │   │   │
├── │   │   │   └───js
├── │   │   │           bootstrap.bundle.min.js
├── │   │   │
├── │   │   ├───temp
├── │   │   ├───templates
├── │   │   │   └───resend
├── │   │   │           base.html
├── │   │   │           change_status.html
├── │   │   │           files_egrn_egrip_egrul_input.html
├── │   │   │           files_input.html
├── │   │   │           files_input_efs_to_spu.html
├── │   │   │           files_input_soe.html
├── │   │   │           file_input.html
├── │   │   │           get_szv_zapros.html
├── │   │   │           index.html
├── │   │   │           journal.html
├── │   │   │           list_input.html
├── │   │   │           login.html
├── │   │   │           navbar.html
├── │   │   │           resend_log_report.html
├── │   │   │           resend_result.html
├── │   │   │           search_szv_zapros.html
├── │   │   │           uspn_input.html
├── │   │   │
├── │   │   ├───uploads
├── │   │   │
├── │   │   ├───utilities
├── │   │
├── │
├── ├───tests
├── │   └───__init__.py
├── │           test_basic.py
└── │

## Database Structure
## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)

![alt text](https://github.com/[username]/[reponame]/blob/[branch]/image.jpg?raw=true)
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

