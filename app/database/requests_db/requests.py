from app.database.models import SessionLocal
from app.database.models import (GameCategory, CategoryItem, ItemToBuy, Photo)
from sqlalchemy import select
from app.cache.redis_cache import cached, build_key


async def get_game_categories():
    async with SessionLocal() as session:
        return await session.scalars(select(GameCategory))


async def get_category_items(category_id):
    async with SessionLocal() as session:
        return await session.scalars(select(CategoryItem).where(CategoryItem.game_category_id == int(category_id)))


async def get_item(category_id):
    async with SessionLocal() as session:
        return await session.scalars(select(ItemToBuy).where(ItemToBuy.category_item_id == int(category_id)))


@cached(key_builder=lambda item_id: build_key(item_id))
async def get_item_details_by_id(item_id):
    async with SessionLocal() as session:
        return await session.scalar(select(ItemToBuy).where(ItemToBuy.item_id == int(item_id)))


@cached(key_builder=lambda item_id: build_key(item_id))
async def get_item_photo_by_id(item_id):
    async with SessionLocal() as session:
        return await session.scalar(select(Photo.photo_google_id).where(Photo.photo_id == int(item_id)))
