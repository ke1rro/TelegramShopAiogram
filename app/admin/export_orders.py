from aiogram import F, Router

from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import OrderByCard
from app.database.requests_db.request_by_card import get_all_orders, get_all_orders_count
from app.utils.export_orders import convert_orders_to_csv


export_orders_router = Router()


@export_orders_router.callback_query(F.data == 'get_all_orders')
async def export_orders_handler(callback: CallbackQuery, session: AsyncSession) -> None:
    all_orders: list[OrderByCard] = await get_all_orders(session=session)
    document: BufferedInputFile = await convert_orders_to_csv(all_orders)
    count: int = await get_all_orders_count(session=session)
    await callback.answer()
    await callback.message.answer_document(document=document, caption=f"order counter:{count}")
