from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.requests_db.requests import get_game_categories, get_category_items

cancel_kb = InlineKeyboardButton(text='Відмінити', callback_data='cancel')

cancel_markup = InlineKeyboardMarkup(inline_keyboard=[
    [cancel_kb]
])

set_game_photo_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Встановити стандартне зображення', callback_data='defaultgame')],
    [InlineKeyboardButton(text='Додати зображення', callback_data='1set_game')],
    [InlineKeyboardButton(text='Відмінити', callback_data='cancel')]])

set_ingame_photo_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Встановити стандартне зображення', callback_data='defaultingame')],
    [InlineKeyboardButton(text='Додати зображення', callback_data='2set_ingame')],
    [InlineKeyboardButton(text='Відмінити', callback_data='cancel')]])


async def game_categories():
    all_games = await get_game_categories()
    keyboard = InlineKeyboardBuilder()

    for game in all_games:
        keyboard.add(InlineKeyboardButton(text=game.category_name, callback_data=f'game_{game.category_name}_{game.id}'))
    keyboard.add(cancel_kb)
    return keyboard.adjust(2).as_markup()


async def category_items(category_id):
    all_category_items = await get_category_items(category_id=category_id)
    keyboard = InlineKeyboardBuilder()

    for category_item in all_category_items:
        keyboard.add(InlineKeyboardButton(text=category_item.category_item_name,
                                          callback_data=f'ingame_{category_item.category_item_id}_{category_item.category_item_name}_{category_item.game_category_id}'))
    keyboard.add(cancel_kb)
    return keyboard.adjust(2).as_markup()

