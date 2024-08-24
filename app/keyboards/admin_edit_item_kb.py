from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app.database.requests_db.requests import get_game_categories, get_category_items, get_item

cancel_kb = InlineKeyboardButton(text='Відмінити', callback_data='cancel')

action = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Змінити ціну', callback_data='edit_item_price')],
    [InlineKeyboardButton(text='Змінити назву', callback_data='edit_item_name')],
    [InlineKeyboardButton(text='Змінити опис', callback_data='edit_item_description')],
    [InlineKeyboardButton(text='Назад', callback_data='admin_back')]])


async def game_categories(prefix: str):
    all_games = await get_game_categories()
    keyboard = InlineKeyboardBuilder()

    for game in all_games:
        keyboard.add(InlineKeyboardButton(text=game.category_name, callback_data=f'{prefix}_game_{game.category_name}_{game.id}'))
    keyboard.row(cancel_kb)
    return keyboard.as_markup()


async def category_items(category_id, prefix: str):
    all_category_items = await get_category_items(category_id=category_id)
    keyboard = InlineKeyboardBuilder()

    for category_item in all_category_items:
        keyboard.add(InlineKeyboardButton(text=category_item.category_item_name,
                                          callback_data=f'{prefix}_{category_item.category_item_id}_{category_item.category_item_name}_{category_item.game_category_id}'))
    keyboard.row(cancel_kb)
    return keyboard.as_markup()


async def get_items_names(category_id: int, prefix: str):
    all_items_names = await get_item(category_id=category_id)
    keyboard = InlineKeyboardBuilder()
    for item_name in all_items_names:
        keyboard.add(InlineKeyboardButton(text=item_name.item_name,
                                          callback_data=f'{prefix}_{item_name.item_id}_{item_name.item_name}'))
    keyboard.row(cancel_kb)
    return keyboard.as_markup()
