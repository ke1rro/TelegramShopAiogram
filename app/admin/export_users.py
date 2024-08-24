from aiogram import F, Router

from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.requests_db.user_requests import get_all_users, get_user_count
from app.utils.export_users import convert_users_to_csv
from app.database.models import User


export_users_router = Router()


@export_users_router.callback_query(F.data == 'get_all_users')
async def export_users_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    all_users: list[User] = await get_all_users(session)
    document: BufferedInputFile = await convert_users_to_csv(all_users)
    count: int = await get_user_count(session)
    await callback.answer()
    await callback.message.answer_document(document=document, caption=f"user counter:{count}")
