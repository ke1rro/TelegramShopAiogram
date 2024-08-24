from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import SessionLocal, GameCategory, CategoryItem, ItemToBuy, Photo
from app.utils.delete_photos import delete_photo
from app.logger.log_maker import logger
from app.cache.redis_cache import clear_cache
from app.database.requests_db.requests import get_item_photo_by_id, get_item_details_by_id
from app.google_drive.google_cdn import delete_file

async def get_game_photo(category_id):
    async with SessionLocal() as session:
        query = await session.scalar(select(GameCategory).where(GameCategory.id == int(category_id)))
        if query:
            if query.photo_id == 'Shop.jpg':
                return 'Shop.jpg'
            return str(f'{query.photo_id}.jpg')
        else:
            return 'Shop.jpg'


async def get_ingame_photo(category_id):
    async with SessionLocal() as session:
        query = await session.scalar(select(CategoryItem).where(CategoryItem.category_item_id == int(category_id)))
        if query:
            if query.photo_id == 'Shop.jpg':
                return 'Shop.jpg'
            return str(f'{query.photo_id}.jpg')
        else:
            return 'Shop.jpg'


async def get_old_gm_photo(game_category_id):
    async with SessionLocal() as session:
            old_photo = await session.scalar(select(GameCategory.photo_id).where(GameCategory.id == int(game_category_id)))
            return str(old_photo)


async def get_old_ingm_photo(category_id, game_category_id):
    async with SessionLocal() as session:
        old_photo = await session.scalar(select(CategoryItem.photo_id).where(CategoryItem.category_item_id == int(category_id) and CategoryItem.game_category_id == int(game_category_id)))
        return str(old_photo)


async def get_old_item_photo(game_category_id, category_id, item_id):
    async with SessionLocal() as session:
        old_photo = await session.scalar(select(ItemToBuy.photo_id).where(ItemToBuy.item_id == int(item_id) and ItemToBuy.category_item_id == int(category_id) and ItemToBuy.game_category_id == int(game_category_id)))
        return str(old_photo)


async def replace_old_gm_photo(game_category_id, new_photo_id):
    async with SessionLocal() as session:
        try:
            game_category = await session.scalar(select(GameCategory).where(GameCategory.id == int(game_category_id)))
            if game_category:
                delete_photo(str(game_category.photo_id))
                game_category.photo_id = new_photo_id
                await session.commit()
                return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)


async def replace_olg_ingm_photo(category_id, new_photo_id):
    async with SessionLocal() as session:
        try:
            category = await session.scalar(select(CategoryItem).where(CategoryItem.category_item_id == int(category_id)))
            if category:

                delete_photo(str(category))
                category.photo_id = new_photo_id
                await session.commit()
                return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)


async def replace_old_item_photo(category_id, item_id, new_photo):
    async with SessionLocal() as session:
        try:
            item = await session.scalar(select(ItemToBuy).where((ItemToBuy.category_item_id == int(category_id)) & (ItemToBuy.item_id == int(item_id))))

            if item:
                photo_id = item.photo_id
                photo_google_id = await session.scalar(select(Photo).where(Photo.photo_id == photo_id))
                if photo_google_id:
                    await delete_file(photo_google_id.photo_google_id)
                    photo_google_id.photo_google_id = new_photo
                    await clear_cache(get_item_details_by_id, item_id)
                    await clear_cache(get_item_photo_by_id, item_id)
                    await session.commit()
                    return True
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(e)