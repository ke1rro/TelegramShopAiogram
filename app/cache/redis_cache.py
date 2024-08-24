from typing import Any, Callable
from redis import asyncio as aioredis
from datetime import timedelta
from redis.asyncio import Redis
from app.cache.serialization import AbstractSerializer, PickleSerializer
from functools import wraps

redis = aioredis.Redis(host='redis', port=6379)
DEFAULT_TTL = 0


def build_key(*args: tuple[str, Any], **kwargs: dict[str: Any]) -> str:
    args_str = ":".join(map(str, args))
    kwargs_str = ":".join(f"{key}={value}" for key, value in sorted(kwargs.items()))
    return f"{args_str}:{kwargs_str}"


async def set_redis_value(
    key: bytes | str, value: bytes | str, ttl: int | timedelta | None = DEFAULT_TTL, is_transaction: bool = False
) -> None:
    async with redis.pipeline(transaction=is_transaction) as pipeline:
        await pipeline.set(key, value)
        if ttl:
            await pipeline.expire(key, ttl)

        await pipeline.execute()


def cached(
    ttl: int | timedelta = DEFAULT_TTL,
    namespace: str = "main",
    cache: Redis = redis,
    key_builder: Callable[..., str] = build_key,
    serializer: AbstractSerializer | None = None,
) -> Callable:
    if serializer is None:
        serializer = PickleSerializer()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: tuple[str, Any], **kwargs: dict[str, Any]) -> Any:
            key = key_builder(*args, **kwargs)
            key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"
            cached_value = await cache.get(key)
            if cached_value is not None:
                return serializer.deserialize(cached_value)

            result = await func(*args, **kwargs)
            await set_redis_value(
                key=key,
                value=serializer.serialize(result),
                ttl=ttl,
            )

            return result

        return wrapper

    return decorator


async def clear_cache(
    func: Callable,
    *args: Any,
    **kwargs: Any,
) -> None:
    namespace: str = kwargs.get("namespace", "main")
    if args or kwargs:
        key = build_key(*args, **kwargs)
        key = f"{namespace}:{func.__module__}:{func.__name__}:{key}"
        await redis.delete(key)
    else:
        pattern = f"{namespace}:{func.__module__}:{func.__name__}:*"
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
