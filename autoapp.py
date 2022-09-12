# -*- coding: utf-8 -*-
"""Create an application instance."""
from flaskshop.app import create_app
from flaskshop.settings import config
from os import environ as env

environment = env.get("FLASK_ENV", "development")
print(environment)
conf = config[environment]
print(conf.SQLALCHEMY_DATABASE_URI)
app = create_app(conf)
