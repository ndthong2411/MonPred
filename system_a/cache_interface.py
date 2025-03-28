import redis, os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = 6379

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def set_price(key, value):
    r.set(key, value)

def set_global_market(key, value):
    r.set(key, value)

def set_sentiment(key, value):
    r.set(key, value)

def get_value(key):
    return r.get(key)
