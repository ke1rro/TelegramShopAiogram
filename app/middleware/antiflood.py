from typing import Any, Dict, Callable, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from redis.asyncio import Redis


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis_storage: Redis):
        self.storage = redis_storage
        self.count = 0
        self.limit = 4
        self.ttl = 10

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: dict[str, Any]
                       ) -> Any:
        user = f'user:{event.from_user.id}'

        user_exists = await self.storage.hexists(name=user, key='user_id')

        if not user_exists:
            user_info = await self.storage.hset(name=user, mapping={'user_id': f'{event.from_user.id}',
                                                                    'count': f'{self.count}'})
            await self.storage.expire(name=user, time=self.ttl)
            return await handler(event, data)
        else:
            count = await self.storage.hget(name=user, key='count')

            if int(count) >= self.limit:

                await event.bot.send_message(chat_id=event.from_user.id,
                                             text='Занадто багато запитів спробуйте через 20 секунд')
                await self.storage.expire(name=user, time=self.ttl)
                return None
            await self.storage.hincrby(name=user, key='count', amount=1)

        return await handler(event, data)
