from flask import Flask
from redis import Redis
from flask_extenstion import FlaskExtension
from .config import RedisConfig
from .mocker import Fake


class FlaskRedis(FlaskExtension):
    redis: Redis
    config: RedisConfig

    def init_app(self, app: Flask):
        if app.config["USE_REDIS"]:
            self.config = RedisConfig(app.config)
            self.redis = Redis.from_url(self.config.REDIS_URL)
        else:
            self.redis = Fake()
