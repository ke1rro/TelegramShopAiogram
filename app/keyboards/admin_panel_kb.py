from emoji import emojize
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

admin_commands = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=emojize('Додати товар :plus:'),
                          callback_data='create_product'),
     InlineKeyboardButton(text=emojize('Видалити товар :wastebasket:'),
                          callback_data='delete_product')],
    [InlineKeyboardButton(text=emojize('Cписок користувачів :clipboard:'),
                          callback_data='get_all_users'),
     InlineKeyboardButton(text=emojize('Cписок замовлень :shopping_cart:'), callback_data='get_all_orders')],
    [InlineKeyboardButton(text='Редагувати товар', callback_data='edit_item')],
    [InlineKeyboardButton(text='Редагувати фото', callback_data='EDIT_photos')],
    [InlineKeyboardButton(text='Назад', callback_data='back')]])
