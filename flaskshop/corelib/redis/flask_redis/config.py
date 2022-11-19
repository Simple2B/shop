from pydantic import BaseModel, RedisDsn


class RedisConfig(BaseModel):
    REDIS_URL: RedisDsn
