import functools
from flask import request
from flask_caching import Cache
import json

class CachedRoute:
    def __init__(self, app):
        self.app = app
        self.cache = Cache(self.app)

    def cached_route(self, timeout=300):
        def decorator(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                cache_key = request.full_path + json.dumps(request.get_json())
                if cache_key not in self.cache:
                    result = f(*args, **kwargs)
                    self.cache.set(cache_key, result, timeout=timeout)
                return self.cache.get(cache_key)
            return decorated_function
        return decorator
