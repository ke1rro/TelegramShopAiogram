from aiogram.filters import BaseFilter
from aiogram.types import Message
from app.database.requests_db.user_requests import check_admin


class AdminChecker(BaseFilter):
    async def __call__(self, message: Message):
        try:
            return await check_admin(message.from_user.id)
        except Exception:
            return False
