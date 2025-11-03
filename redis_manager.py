# redis_manager_async.py
import os
import json
import asyncio
from aioredis import Redis, from_url

# -------------------------
# Redis connection
# -------------------------
UPSTASH_URL = os.getenv("UPSTASH_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_TOKEN")  # Optional if using rediss:// URL

r: Redis = None  # Will initialize in async function

async def init_redis():
    global r
    r = from_url(
        UPSTASH_URL,
        decode_responses=True,
        username="default",
        password=UPSTASH_TOKEN
    )
    print("Redis connection established.")

# -------------------------
# Config per queue
# -------------------------
QUEUES_CONFIG = {
    "default_queue": {"max_size": 200, "ttl": 86400},  # 24 hours
    "failed_pushes": {"max_size": 100, "ttl": 604800}, # 7 days
}

AUTOMATIC_CLEAN_INTERVAL = 300  # 5 minutes
MAX_MEMORY_BYTES = 256 * 1024 * 1024  # 256 MB
SOFT_EVICTION_RATIO = 0.8

# -------------------------
# Queue helpers
# -------------------------
async def add_to_queue(queue_name: str, data: dict):
    cfg = QUEUES_CONFIG.get(queue_name, {"max_size": 100, "ttl": 86400})
    payload = json.dumps(data, separators=(",", ":"))
    await r.lpush(queue_name, payload)
    await r.expire(queue_name, cfg["ttl"])

    if await r.llen(queue_name) > int(cfg["max_size"] * SOFT_EVICTION_RATIO):
        await trim_queue(queue_name, cfg["max_size"])

async def pop_from_queue(queue_name: str):
    item = await r.rpop(queue_name)
    return json.loads(item) if item else None

async def trim_queue(queue_name: str, max_size: int):
    await r.ltrim(queue_name, 0, max_size - 1)

# -------------------------
# Cleanup
# -------------------------
async def cleanup():
    for queue_name, cfg in QUEUES_CONFIG.items():
        if await r.llen(queue_name) > cfg["max_size"]:
            await trim_queue(queue_name, cfg["max_size"])

    # Optional memory-aware cleanup
    info = await r.info()
    used_memory = info.get("used_memory", 0)
    if used_memory > MAX_MEMORY_BYTES * 0.9:
        print(f"[Warning] Redis memory {used_memory} exceeds 90% of limit. Soft trimming queues...")
        for queue_name, cfg in QUEUES_CONFIG.items():
            while await r.llen(queue_name) > int(cfg["max_size"] * 0.5):
                await r.rpop(queue_name)

# -------------------------
# Background cleanup loop
# -------------------------
async def background_cleanup_loop():
    while True:
        await cleanup()
        await asyncio.sleep(AUTOMATIC_CLEAN_INTERVAL)

# -------------------------
# Monitoring
# -------------------------
async def print_queue_status():
    for queue_name in QUEUES_CONFIG:
        count = await r.llen(queue_name)
        print(f"{queue_name}: {count} items")

# -------------------------
# Example usage
# -------------------------
async def main():
    await init_redis()
    # Start background cleanup in the background
    asyncio.create_task(background_cleanup_loop())

    await add_to_queue("default_queue", {"msg": "Hello async Redis!"})
    await add_to_queue("failed_pushes", {"msg": "Failed push async test"})
    
    popped = await pop_from_queue("default_queue")
    print("Popped:", popped)
    await print_queue_status()

if __name__ == "__main__":
    asyncio.run(main())
