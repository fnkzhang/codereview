from flask_caching import Cache

cacheConfig = {
    "CACHE_TYPE": "SimpleCache"
}

def initCache(app):
    global cache
    cache = Cache(app, config=cacheConfig)

def getValueFromCache(key):
    return cache.get(key)

def addToCacheWithTimeout(key, value, timeout):
    cache.set(key, value, timeout)