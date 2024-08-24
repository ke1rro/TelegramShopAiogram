from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards import admin_delete_kb as kb
from app.database.requests_db.delete_products_requests import (delete_game_category,
                                                               delete_ingame_category, delete_item_from_db)

delete_products_router = Router()


@delete_products_router.callback_query(F.data == 'delete_product')
async def choose_delete_section(callback: CallbackQuery):
    await callback.message.edit_caption(caption='Оберіть конкретну дію видалення', reply_markup=kb.delete_actions)


@delete_products_router.callback_query(F.data == 'del_game')
async def choose_gm_category_to_del(callback: CallbackQuery):
    await callback.message.edit_caption(caption='Оберіть ігрову категорію для видалення',
                                        reply_markup=await kb.game_categories(prefix='delete'))


@delete_products_router.callback_query(F.data.startswith('delete'))
async def game_category_to_del(callback: CallbackQuery):
    game_category = callback.data.split('_')
    game_category_name = game_category[2]
    game_category_id = int(game_category[3])
    if await delete_game_category(game_category_id=game_category_id):
        await callback.answer()
        await callback.message.answer(text=f"Ігрова катоегорія '{game_category_name}' видалена")
    else:
        await callback.answer()
        await callback.message.answer(text=f"Ігрова катоегорія '{game_category_name}' не видалена")


@delete_products_router.callback_query(F.data == 'del_ingame')
async def choose_gm_category(callback: CallbackQuery):
    await callback.message.edit_caption(caption='Оберіть ігрову категорію',
                                        reply_markup=await kb.game_categories(prefix='choosegame'))


@delete_products_router.callback_query(F.data.startswith('choosegame_'))
async def choose_ingame_category(callback: CallbackQuery):
    data = callback.data.split('_')
    category_id = int(data[3])
    await callback.message.edit_caption(caption='Оберіть підкатегорію для видалення',
                                        reply_markup=await kb.category_items(category_id=category_id,
                                                                             prefix='ingamedelete_'))


@delete_products_router.callback_query(F.data.startswith('ingamedelete_'))
async def delete_category_items(callback: CallbackQuery):
    data = callback.data.split('_')
    category_item_id = int(data[2])
    category_item_name = data[3]
    if await delete_ingame_category(category_item_id=category_item_id):
        await callback.answer()
        await callback.message.answer(text=f"Підкатегорія '{category_item_name}' видалена")
    else:
        await callback.answer()
        await callback.message.answer(text=f"Підкатегорія '{category_item_name}' не видалена")


@delete_products_router.callback_query(F.data == 'del_item')
async def choose_game_category_for_item(callback: CallbackQuery):
    await callback.message.edit_caption(caption='Оберіть ігрову категорію',
                                        reply_markup=await kb.game_categories(prefix='itemdel'))


@delete_products_router.callback_query(F.data.startswith('itemdel_'))
async def choose_ingame_category_for_item(callback: CallbackQuery):
    data = callback.data.split('_')
    game_category_id = int(data[3])
    await callback.message.edit_caption(caption='Оберіть підкатегорію',
                                        reply_markup=await kb.category_items(category_id=game_category_id,
                                                                             prefix='todelitem'))


@delete_products_router.callback_query(F.data.startswith('todelitem'))
async def chose_item_to_del(callback: CallbackQuery):
    data = callback.data.split('_')
    ingame_category_id = int(data[1])
    await callback.message.edit_caption(caption='Оберіть товар для видалення',
                                        reply_markup=await kb.get_items_names(category_id=ingame_category_id,
                                                                              prefix='choosenitem'))


@delete_products_router.callback_query(F.data.startswith('choosenitem_'))
async def delete_item(callback: CallbackQuery):
    data = callback.data.split('_')
    item_id = int(data[1])
    item_category_item = int(data[3])
    item_game_category = int(data[4])
    if await delete_item_from_db(item_id=item_id, game_category_id=item_game_category,
                                 category_item_id=item_category_item):
        await callback.answer()
        await callback.message.answer(text="Товар видалено")
    else:
        await callback.answer()
        await callback.message.answer(text="Сталась помилка товар не видалено")
