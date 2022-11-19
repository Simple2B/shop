from .local_cache import LocalCache
from .redis import FlaskRedis

lc = LocalCache()
rdb = FlaskRedis()
