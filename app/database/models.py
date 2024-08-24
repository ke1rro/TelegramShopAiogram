import os
from dotenv import load_dotenv
from sqlalchemy import Integer, String, BigInteger, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import (AsyncAttrs,
                                    async_sessionmaker, create_async_engine)

load_dotenv()
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
print(POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER)

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


engine = create_async_engine(url=DATABASE_URL, pool_pre_ping=True)
SessionLocal = async_sessionmaker(autoflush=False, bind=engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, nullable=False, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(32), nullable=True)
    money_balance: Mapped[int] = mapped_column(Integer, nullable=True, default=0)


class GameCategory(Base):
    __tablename__ = 'game_categories'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, nullable=False, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True,)
    photo_id: Mapped[str] = mapped_column(String, nullable=False, default='Shop.jpg')

class CategoryItem(Base):
    __tablename__ = 'category_items'
    category_item_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True,
                                                  nullable=False, autoincrement=True)
    category_item_name: Mapped[str] = mapped_column(String(64), nullable=False)
    game_category_id: Mapped[int] = mapped_column(Integer, ForeignKey('game_categories.id', ondelete='CASCADE'),
                                                  nullable=False)
    photo_id: Mapped[str] = mapped_column(String, nullable=False, default='Shop.jpg')

class ItemToBuy(Base):
    __tablename__ = 'items_to_buy'
    item_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    item_name: Mapped[str] = mapped_column(String(64), nullable=False)
    item_price: Mapped[int] = mapped_column(Integer, nullable=False)
    item_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    item_description: Mapped[str] = mapped_column(Text, nullable=True)
    category_item_id: Mapped[int] = mapped_column(Integer, ForeignKey('category_items.category_item_id',
                                                                      ondelete='CASCADE'), nullable=False)
    game_category_id: Mapped[int] = mapped_column(Integer, ForeignKey('game_categories.id',
                                                                      ondelete='CASCADE'))
    photo_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('photos.photo_id', ondelete='CASCADE'),
                                          nullable=True)


class Photo(Base):
    __tablename__ = 'photos'
    photo_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    photo_google_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey('items_to_buy.item_id', ondelete='CASCADE'))


class OrderByCard(Base):
    __tablename__ = 'orders_by_cards'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    customer_tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    customer_phone: Mapped[str] = mapped_column(String, nullable=False)
    item_name: Mapped[str] = mapped_column(String, nullable=False)
    item_price: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[str] = mapped_column(String, nullable=False)


class Admin(Base):
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(32), nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
