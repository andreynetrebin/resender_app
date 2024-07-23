from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = environ.get("SECRET_KEY")
    FLASK_SECRET = SECRET_KEY
    LOGFILENAME = "resender.log"


class DevConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DATABASE = path.join(basedir, "dev_app.db")
    LOGGING_LEVEL = 'DEBUG'


class ProdConfig(Config):
    DEBUG = False
    DEVELOPMENT = False
    DATABASE = path.join(basedir, "app.db")
    LOGGING_LEVEL = 'INFO'


class TestingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    TESTING = True
    DATABASE = path.join(basedir, "test_app.db")


configuration = {
    "dev": DevConfig,
    "prod": ProdConfig,
    "default": DevConfig,
    "testing": TestingConfig
}
