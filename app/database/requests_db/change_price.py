from typing import Any
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.logger.log_maker import logger
from app.database.models import SessionLocal, ItemToBuy
from app.cache.redis_cache import clear_cache
from app.database.requests_db.requests import get_item_details_by_id


async def edit_item(item_id: int, edit_selector: Any, prefix: str) -> bool:
    async with SessionLocal() as session:
        try:
            query = await session.scalar(select(ItemToBuy).where(ItemToBuy.item_id == item_id))
            if query:
                setattr(query, prefix, edit_selector)
                logger.info(f"Item changed: {query.item_name} prefix: {prefix} edit_selector: {edit_selector}")
                await session.flush()
                await session.commit()
                await clear_cache(get_item_details_by_id, item_id)
                return True
            return False
        except SQLAlchemyError:
            logger.error(f"Failed to edit item {item_id}, prefix: {prefix}, edit_selector: {edit_selector}")
            await session.rollback()
