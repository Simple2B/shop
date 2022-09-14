# -*- coding: utf-8 -*-
"""Application configuration."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


# class LocalConfig:
#     db_type = os.getenv("DB_TYPE", "mysql")
#     user = os.getenv("DB_USER", "postgres")
#     passwd = os.getenv("DB_PASSWD", "secret")
#     # host = os.getenv("DB_HOST", "127.0.0.1")
#     port = os.getenv("LOCAL_DB_PORT", 3306)
#     db_name = os.getenv("DB_NAME", "db")
#     if db_type == "postgresql":
#         db_uri = "postgresql://{user}:{passwd}@{host}:5432/{db_name}".format(
#             user=user, passwd=passwd, host=host, db_name=db_name
#         )
#     elif db_type == "mysql":
#         db_uri = "mysql+pymysql://{user}:{passwd}@{host}:{port}/{db_name}?charset=utf8mb4".format(
#             user=user, passwd=passwd, host=host, port=port, db_name=db_name
#         )
#     # redis_uri = "redis://127.0.0.1:6379"
#     # esearch_uri = "localhost:9200"
#     redis_uri = "redis://redis:6379"
#     esearch_uri = "http://localhost:9200"


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY", "Ensure you set a secret key, this is important!"
    )
    # Redis
    # if redis is enabled, it can be used for:
    #   - cache
    #   - save product description
    #   - save page content
    USE_REDIS = int(os.getenv("USE_REDIS", 0)) == 1
    REDIS_URL = os.getenv(
        "REDIS_URI",
    )

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID")
    # Elasticsearch
    # if elasticsearch is enabled, the home page will have a search bar
    # and while add a product, the search index will get update
    USE_ES = int(os.getenv("USE_ES", 0)) == 1
    ES_HOSTS = [os.getenv("ESEARCH_URI")]
    # SQLALCHEMY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE_QUERY_TIMEOUT = 0.1  # log the slow database query, and unit is second
    SQLALCHEMY_RECORD_QUERIES = True
    # Dir
    APP_DIR = Path(__file__).parent  # This directory
    PROJECT_ROOT = APP_DIR.parent
    STATIC_DIR = APP_DIR / "static"
    UPLOAD_FOLDER = "upload"
    UPLOAD_DIR = STATIC_DIR / UPLOAD_FOLDER
    DASHBOARD_TEMPLATE_FOLDER = APP_DIR / "templates" / "dashboard"
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "static/placeholders")
    PURCHASE_URI = os.getenv("PURCHASE_URI", "")
    BCRYPT_LOG_ROUNDS = 13

    MESSAGE_QUOTA = 10
    LANGUAGES = {"en": "English", "bg": "Български"}
    BABEL_DEFAULT_LOCALE = os.getenv("BABEL_DEFAULT_LOCALE", "en_US")
    BABEL_DEFAULT_TIMEZONE = os.getenv("BABEL_DEFAULT_TIMEZONE", "UTC")
    BABEL_TRANSLATION_DIRECTORIES = os.getenv(
        "BABEL_TRANSLATION_DIRECTORIES", "../translations"
    )
    BABEL_CURRENCY = os.getenv("BABEL_CURRENCY", "USD")
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = os.getenv("MAIL_PORT", 25)
    MAIL_TLS = int(os.getenv("MAIL_TLS", 0)) == 1
    if MAIL_TLS:
        MAIL_USE_TLS = True
        MAIL_USE_SSL = False
    else:
        MAIL_USE_TLS = False
        MAIL_USE_SSL = True

    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "")
    GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_ACCESS_TOKEN_URL = "https://accounts.google.com/o/oauth2/token"
    FACEBOOK_APP_ID = os.getenv("FACEBOOK_AP_ID")


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + str(
        (Path(__file__).parent.parent / "database-test.sqlite3")
    )
    DEBUG = True
    WTF_CSRF_ENABLED = False
    DEBUG_TB_ENABLED = int(os.getenv("FLASK_DEBUG", 0)) == 1
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    MAIL_DEBUG = DEBUG_TB_ENABLED


class DevConfig(Config):
    ENV = "development"
    DEBUG = True
    DEBUG_TB_ENABLED = int(os.getenv("FLASK_DEBUG", 0)) == 1
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    MAIL_DEBUG = DEBUG_TB_ENABLED
    AUTHLIB_INSECURE_TRANSPORT = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DB_URI",
        "sqlite:///" + str((Path(__file__).parent.parent / "database-test.sqlite3")),
    )


class ProdConfig(Config):
    ENV = "production"
    DEBUG = False
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DB_URI")


config = {config_class.ENV: config_class for config_class in (DevConfig, ProdConfig)}
