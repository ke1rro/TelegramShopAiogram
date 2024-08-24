
from emoji import emojize
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton)
from app.database.requests_db.requests import get_game_categories, get_category_items, get_item

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=emojize('Магазин :shopping_cart:'),
                          callback_data='shop'),
     InlineKeyboardButton(text=emojize('Профіль :bust_in_silhouette:'),
                          callback_data='account')],
    [InlineKeyboardButton(text=emojize('FAQ :red_question_mark:'),
                          callback_data='FAQ'),
     InlineKeyboardButton(text=emojize('Гарантії :shield:'),
                          callback_data='guarantees')],
    [InlineKeyboardButton(text=emojize('Відгуки :star:'),
                          callback_data='reviews'),
     InlineKeyboardButton(text=emojize('Підтримка :telephone:'),
                          callback_data='support')]
])

back_button = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='Назад', callback_data='back')
]], )

phone_num_request = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=emojize('Поділитись контактом :check_mark_button:'),
                    request_contact=True)]], one_time_keyboard=True, resize_keyboard=True)

check_subscription = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Підписатись', url='URL TO YOUR CHANNEL')],
    [InlineKeyboardButton(text=emojize('Перевірити підписку :check_mark_button:'), callback_data='check_sub')]])

cancel_order = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Відмінити замовлення', callback_data='ORDCANCEL')]])


async def game_categories():
    all_games = await get_game_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_games:
        keyboard.row(InlineKeyboardButton(text=category.category_name,
                                          callback_data=f'category_{category.id}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data='back'))
    return keyboard.as_markup()


async def category_items(category_id):
    all_category_items = await get_category_items(category_id=category_id)
    keyboard = InlineKeyboardBuilder()

    for category_item in all_category_items:
        keyboard.row(InlineKeyboardButton(text=category_item.category_item_name,
                                          callback_data=f'Ingameitem_{category_item.category_item_id}'))
    keyboard.row(InlineKeyboardButton(text='Назад', callback_data='back_to_game_categories'))
    return keyboard.as_markup()


async def get_items_names(category_id):
    all_items_names = await get_item(category_id=category_id)
    keyboard = InlineKeyboardBuilder()

    for item_name in all_items_names:
        keyboard.row(InlineKeyboardButton(text=item_name.item_name,
                                          callback_data=f'item_{category_id}_{item_name.item_id}'))
    keyboard.row(InlineKeyboardButton(text='Назад',
                                      callback_data=f'back_to_category_{category_id}_{item_name.game_category_id}'))
    return keyboard.as_markup()
