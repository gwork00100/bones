# test_redis.py
import os
from redis import Redis

# Read Redis URL and token from environment variables
redis_url = os.getenv("UPSTASH_URL")
redis_token = os.getenv("UPSTASH_TOKEN")

r = Redis.from_url(
    redis_url,
    decode_responses=True,
    username="default",
    password=redis_token
)

# Test: set and get a value
r.set("hello", "world")
print("Redis test value:", r.get("hello"))
