import hashlib
import time
from typing import Optional
import redis


from config import settings


redis_cache = None

def get_redis_cache()-> redis.Redis:
    global redis_cache

    if redis_cache is None:
        redis_cache = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            decode_responses=True,
            username=settings.redis_username,
            password=(settings.redis_password.get_secret_value()
                      if settings.redis_password else None),
        )
        return redis_cache
    else:
        return redis_cache


class Cache:
    def __init__(self, ttl_seconds : int = 30):
        self.ttl = ttl_seconds
        self.redis_db = get_redis_cache()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _make_key(query: str)-> str:
        """ Create a cache key from normalized query."""
        normalized = query.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def get(self,query)-> Optional[str]:
        key = self._make_key(query)
        obj = self.redis_db.hgetall(key)
        query_response = obj.get('response')
        if query_response:
            self._hits += 1
            return str(query_response)
        else:
            self._misses += 1
            return None

    def set(self,query: str, response: str):
        """ Cache a response into Redis DB """
        key = self._make_key(query)
        self.redis_db.hset(key,mapping={
            'query': query,
            'response' : response,
        },)
        self.redis_db.expire(name=key,time=self.ttl)




    @property
    def get_stats(self):
        pass






