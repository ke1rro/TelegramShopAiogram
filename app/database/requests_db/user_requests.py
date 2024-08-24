from sqlalchemy.ext.asyncio import AsyncSession
from app.cache.redis_cache import build_key, cached, clear_cache
from app.database.models import Admin, SessionLocal, User
from app.logger.log_maker import logger

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError


async def check_phone_number(telegram_id: int) -> bool:
    async with SessionLocal() as session:
        user_phone_number = await session.scalar(select(User.phone_number).filter_by(telegram_id=telegram_id).limit(1))
        return None if user_phone_number is None or user_phone_number is False else True


async def get_phone_num_invoice(telegram_id: int) -> str:
    async with SessionLocal() as session:
        user_phone_number = await session.scalar(select(User.phone_number).where(User.telegram_id == telegram_id))
        if user_phone_number:
            return user_phone_number
        else:
            return '0'


async def check_admin(telegram_id):
    async with SessionLocal() as session:
        return await session.scalar(select(Admin).where(Admin.telegram_id == telegram_id))


@cached(key_builder=lambda session, telegram_id: build_key(telegram_id), ttl=500)
async def check_user(session: AsyncSession, telegram_id: int) -> bool:
    async with session() as request:
        user = await request.scalar(select(User.telegram_id).filter_by(telegram_id=telegram_id).limit(1))
        return bool(user)


async def registrate_user(telegram_id, username, first_name):
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        try:
            if not user:
                new_user = User(username=username,
                                first_name=first_name,
                                telegram_id=telegram_id)
                session.add(new_user)
                logger.info(f"New user {new_user.telegram_id}")
                await session.commit()
                await session.refresh(new_user)
                await clear_cache(check_user, telegram_id)
        except SQLAlchemyError as e:
            logger.error(e)


async def update_user_phone_number(telegram_id, phone_number):
    async with SessionLocal() as session:
        try:
            user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

            user.phone_number = phone_number
            await session.commit()
            await session.refresh(user)
            return user
        except SQLAlchemyError as e:
            logger.error(e)


@cached(key_builder=lambda telegram_id: build_key(telegram_id))
async def get_user_balance(telegram_id):
    async with SessionLocal() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if user:
            user_balance = user.money_balance
            return user_balance


@cached(key_builder=lambda session: build_key(), ttl=10)
async def get_all_users(session: AsyncSession) -> list[User]:
    async with session() as sess:
        query = select(User)
        result = await sess.execute(query)
        users = result.scalars().all()
        return users


@cached(key_builder=lambda session: build_key(), ttl=10)
async def get_user_count(session: AsyncSession) -> int:
    async with session() as sess:
        query = select(func.count(User.id))
        result = await sess.execute(query)
        count = result.scalar_one_or_none() or 0
        return int(count)
