import os
import redis
from cachelib.base import BaseCache

class RedisCache(BaseCache):
    """A Redis-based cache implementation."""
    
    def __init__(self, default_timeout=300):
        """Initialize the RedisCache with a default timeout and connection settings."""
        self.default_timeout = default_timeout
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_username = os.getenv('REDIS_USERNAME')
        self.redis_password = os.getenv('REDIS_PASSWORD')
        
        self.pool = redis.ConnectionPool(
            host=self.redis_host,
            port=self.redis_port,
            username=self.redis_username,
            password=self.redis_password,
            decode_responses=True
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def get(self, key):
        """Retrieve a value from the cache by key."""
        try:
            return self.client.get(key)
        except Exception as e:
            self._handle_error(e)

    def set(self, key, value, timeout=None):
        """Set a value in the cache with an optional timeout."""
        try:
            if timeout is None:
                timeout = self.default_timeout
            self.client.set(key, value, ex=timeout)
        except Exception as e:
            self._handle_error(e)

    def delete(self, key):
        """Delete a value from the cache by key."""
        try:
            existed = self.client.exists(key)
            self.client.delete(key)
            return existed > 0
        except Exception as e:
            self._handle_error(e)

    def clear(self):
        """Clear the entire cache."""
        try:
            self.client.flushdb()
            return True
        except Exception as e:
            self._handle_error(e)
            return False

    def has(self, key):
        """Check if a value exists in the cache by key."""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            self._handle_error(e)
            return False

    def add(self, key, value, timeout=None):
        """Add a value to the cache if it does not already exist."""
        if not self.has(key):
            self.set(key, value, timeout)
            return True
        return False

    def set_many(self, mapping, timeout=None):
        """Set multiple values in the cache."""
        for key, value in mapping.items():
            self.set(key, value, timeout)

    def delete_many(self, keys):
        """Delete multiple values from the cache."""
        for key in keys:
            self.delete(key)

    def inc(self, key, delta=1):
        """Increment a value in the cache by a specified delta."""
        return self.client.incr(key, delta)

    def dec(self, key, delta=1):
        """Decrement a value in the cache by a specified delta."""
        return self.client.decr(key, delta)

    def get_many(self, keys):
        """Retrieve multiple values from the cache by keys."""
        try:
            return {key: self.client.get(key) for key in keys}
        except Exception as e:
            self._handle_error(e)

    def get_dict(self, keys):
        """Retrieve multiple values from the cache and return them as a dictionary."""
        try:
            return {key: self.client.get(key) for key in keys}
        except Exception as e:
            self._handle_error(e)