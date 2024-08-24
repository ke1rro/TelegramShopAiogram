from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from datetime import datetime

from app.database.models import (SessionLocal, User, OrderByCard)
from app.logger.log_maker import logger


async def new_order_card(telegram_id: int, order_id: str, customer_name: str, customer_phone: str,
                         item_name: str, item_price: int):
    async with SessionLocal() as session:
        user_exists = await session.scalar(select(User).where(User.telegram_id == int(telegram_id)))
        try:
            if user_exists:
                new_order = OrderByCard(order_id=order_id,
                                        customer_tg_id=telegram_id,
                                        customer_name=customer_name,
                                        customer_phone=customer_phone,
                                        item_name=item_name,
                                        item_price=item_price,
                                        time=str(datetime.now()))
                session.add(new_order)
                logger.info(f"New order {order_id} created")
                await session.flush()
                await session.commit()
                await session.refresh(new_order)
                return new_order
        except SQLAlchemyError as e:
            logger.error(e)
            await session.rollback()


async def check_order(telegram_id: int, order_id: str) -> bool:
    async with SessionLocal() as session:
        order_exist = await session.scalar(select(OrderByCard.customer_tg_id).where(OrderByCard.order_id == order_id and OrderByCard.customer_tg_id == int(telegram_id)))
        if order_exist:
            return order_exist


async def get_all_orders(session: AsyncSession) -> list[OrderByCard]:
    async with session() as session:
        try:
            query = select(OrderByCard)
            result = await session.execute(query)
            orders = result.scalars().all()
            return orders
        except SQLAlchemyError as e:
            logger.error(e)


async def get_all_orders_count(session: AsyncSession):
    async with session() as session:
        try:
            query = select(func.count(OrderByCard.id))
            result = await session.execute(query)
            count = result.scalar_one_or_none() or 0
            return int(count)
        except SQLAlchemyError as e:
            logger.error(e)
