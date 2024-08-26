from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager
import logging
from logging.config import dictConfig
from os import path, makedirs
from typing import Optional
from config import config
from .dict_config import get_dict_config

app_dir = path.abspath(path.dirname(__file__))
logs_dir = path.join(app_dir, "logs")
if not path.exists(logs_dir):
    makedirs(logs_dir)


def create_app(configuration):
    """Создание фабрики приложения. Инициализация приложения
    Args:
        conf (str): Конфигурация
    Returns:
        app (flask.app.Flask):  Приложение Flask
    """

    app = Flask(__name__)
    app.config.from_object(config.get(configuration))
    logging_level = app.config["LOGGING_LEVEL"]
    logging_filename = path.join(logs_dir, app.config["LOGFILENAME"])
    dict_config = get_dict_config(logging_level, logging_filename)
    logging.config.dictConfig(dict_config)
    app.logger.debug("init_app")

    from . import db

    db.init_app(app)

    # создаем объект менеджера и добавляем его в приложение
    login_manager = LoginManager()
    login_manager.init_app(app)
    from .users import User

    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        """Используется для перезагрузки объекта пользователя из идентификатора пользователя, хранящегося в сеансе
        Args:
            user_id (str): ID пользователя
        Returns:
            app (app.users.User):  Объект пользователя
        """
        return User.users.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        """При unauthorized users перенарправлять залогиниться."""
        flash('Вы должны авторизоваться.')
        return redirect(url_for('auth.login'))

    # blueprint для главной страницы
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint.main)

    # blueprint для авторизации/регистрации пользователей
    from .auth import auth as auth_blueprint

    app.register_blueprint(auth_blueprint.auth, url_prefix="/auth")

    # blueprint для админки
    from .admin import admin as admin_blueprint

    app.register_blueprint(admin_blueprint.admin, url_prefix="/admin")

    # blueprint для основного функционала - переотправок сообщений в MQ
    from .resend import resend as resend_blueprint

    app.register_blueprint(resend_blueprint.resend, url_prefix="/resend")

    # blueprint для профиля пользователей
    from .profile import profile as profile_blueprint

    app.register_blueprint(profile_blueprint.profile, url_prefix="/profile")

    # blueprint для API
    from .api import api as api_blueprint

    app.register_blueprint(api_blueprint.api, url_prefix="/api")
    return app
