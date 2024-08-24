import os

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError


from app.database.models import SessionLocal
from app.cache.redis_cache import clear_cache
from app.database.requests_db.requests import get_item_details_by_id, get_item_photo_by_id
from app.google_drive.google_cdn import delete_file, delete_files
from app.logger.log_maker import logger
from app.database.models import (GameCategory, CategoryItem, ItemToBuy, Photo)


async def delete_game_category(game_category_id: int) -> bool:
    async with SessionLocal() as session:
        try:
            query = await session.scalar(select(GameCategory).where(GameCategory.id == game_category_id))
            all_ingames = await session.scalars(select(CategoryItem.photo_id).where(CategoryItem.game_category_id == query.id))
            if not query:
                logger.warning(f'GAME Category with id {query.category_item_name} not found.')
                return False

            games = await session.scalars(select(ItemToBuy).where(ItemToBuy.game_category_id == query.id))
            games = games.all()

            photo_ids = []
            for game in games:
                photos = await session.scalars(select(Photo.photo_google_id).where(Photo.photo_id == game.photo_id))
                photo_ids.extend(photos.all())

            to_delete_gm = query.photo_id
            to_delete_ingm = all_ingames.all()
            if os.path.isfile(f'app/bot_imgs/{to_delete_gm}.jpg') and to_delete_gm != 'Shop':
                os.remove(f'app/bot_imgs/{to_delete_gm}.jpg')

            for photo in to_delete_ingm:
                if os.path.isfile(f'app/bot_imgs/{photo}.jpg') and photo != 'Shop':
                    os.remove(f'app/bot_imgs/{photo}.jpg')

            await delete_files(photo_ids)
            await session.delete(query)
            await session.commit()
            await clear_cache(get_item_photo_by_id)
            await clear_cache(get_item_details_by_id)
            logger.info(f'Game Category deleted successfully {query.category_name}')
            return True
        except SQLAlchemyError as e:
            logger.error(e)
            await session.rollback()


async def delete_ingame_category(category_item_id: int) -> bool:
    async with SessionLocal() as session:
        try:
            query = await session.scalar(select(CategoryItem).where(CategoryItem.category_item_id == category_item_id))
            if not query:
                logger.warning(f'Category with id {query.category_item_name} not found.')
                return False

            games = await session.scalars(select(ItemToBuy).where(ItemToBuy.category_item_id == category_item_id))
            games = games.all()

            photo_ids = []
            for game in games:
                photos = await session.scalars(select(Photo.photo_google_id).where(Photo.photo_id == game.photo_id))
                photo_ids.extend(photos.all())

            photo_to_del = query.photo_id
            if os.path.isfile(f'app/bot_imgs/{photo_to_del}.jpg') and photo_to_del != 'Shop':
                os.remove(f'app/bot_imgs/{photo_to_del}.jpg')

            await delete_files(photo_ids)
            await session.delete(query)
            await session.commit()
            await clear_cache(get_item_photo_by_id)
            await clear_cache(get_item_details_by_id)
            logger.info(f'Ingame Category Delete: {query.category_item_name}')
            return True
        except SQLAlchemyError as e:
            logger.error(e)
            await session.rollback()


async def delete_item_from_db(item_id: int, game_category_id: int, category_item_id: int) -> bool:
    async with SessionLocal() as session:
        try:
            query = await session.scalar(select(ItemToBuy).where(ItemToBuy.item_id == item_id,
                                                                 ItemToBuy.game_category_id == game_category_id,
                                                                 ItemToBuy.category_item_id == category_item_id))
            query_photo = await session.scalar(select(Photo).where(Photo.item_id == item_id))

            await delete_file(query_photo.photo_google_id)
            await clear_cache(get_item_details_by_id, item_id)
            await clear_cache(get_item_photo_by_id, item_id)
            await session.delete(query)
            await session.commit()
            logger.info(f'Item Deleted Successfully: {query.item_name}')
            return True
        except SQLAlchemyError:
            logger.error(f'Failed to Delete Item from DB {query.item_name}')
            await session.rollback()
