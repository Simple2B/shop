from os import environ as env

# -*- coding: utf-8 -*-
"""Create an application instance."""
from flaskshop.app import create_app
from flaskshop.settings import config

from flaskshop.logger import log

environment = env.get("FLASK_ENV", "development")
log(log.INFO, "Running app using [%s] environment", environment)
conf = config[environment]
(log.INFO, "Running app with [%s] db", conf.SQLALCHEMY_DATABASE_URI)
app = create_app(conf)
