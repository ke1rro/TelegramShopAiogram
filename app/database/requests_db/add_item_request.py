from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import SessionLocal, GameCategory, CategoryItem, ItemToBuy, Photo
from app.logger.log_maker import logger


async def add_product_with_photo(item_data):
    async with SessionLocal() as session:
        try:
            game_category_name = item_data["game_category"]
            category_item_name = item_data["category_item_name"]
            item_name = item_data["item_name"]
            item_price = item_data["item_price"]
            item_description = item_data["item_description"]
            photo_google_id = item_data["item_photo_id"]
            standart_photo_game = item_data['game_photo']
            standart_photo_ingame = item_data['ingame_photo']
            new_game_ph = item_data['proceed_game_photo']
            new_ingame_ph = item_data['proceed_ingame_photo']
            game_category = await session.execute(
                select(GameCategory).filter_by(category_name=game_category_name)
            )
            game_category = game_category.scalar_one_or_none()

            if not game_category:
                if standart_photo_game:
                    photo_id = standart_photo_ingame
                else:
                    photo_id = new_game_ph
                new_game_category = GameCategory(category_name=game_category_name, photo_id=photo_id)
                session.add(new_game_category)
                await session.flush()
            else:
                new_game_category = game_category

            category_item = await session.execute(
                select(CategoryItem).filter_by(
                    category_item_name=category_item_name,
                    game_category_id=new_game_category.id
                )
            )
            category_item = category_item.scalar_one_or_none()

            if not category_item:
                if standart_photo_ingame:
                    photo_id = standart_photo_ingame
                else:
                    photo_id = new_ingame_ph
                new_category_item = CategoryItem(
                    category_item_name=category_item_name,
                    game_category_id=new_game_category.id,
                    photo_id=photo_id
                )
                session.add(new_category_item)
                await session.flush()
            else:
                new_category_item = category_item

            new_item = ItemToBuy(
                item_name=item_name,
                item_price=item_price,
                item_quantity=0,
                item_description=item_description,
                category_item_id=new_category_item.category_item_id,
                game_category_id=new_game_category.id
            )

            session.add(new_item)
            logger.info(f"New item added to database {new_item.item_name}")
            await session.flush()
            new_photo = Photo(photo_google_id=photo_google_id, item_id=new_item.item_id)
            session.add(new_photo)
            await session.flush()
            new_item.photo_id = new_photo.photo_id
            await session.flush()
            await session.commit()

        except SQLAlchemyError as e:
            logger.error(e)
            await session.rollback()
