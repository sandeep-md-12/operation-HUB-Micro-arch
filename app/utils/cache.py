import os
import redis.asyncio as aioredis
from dotenv import load_dotenv

load_dotenv()

_REDIS_URL = os.getenv("REDIS_URL")
if not _REDIS_URL:
    raise RuntimeError("REDIS_URL environment variable is not set")

redis_client = aioredis.from_url(_REDIS_URL, decode_responses=True)
