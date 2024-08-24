from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from app.keyboards import admin_edit_item_kb as kb
from app.database.requests_db.change_price import edit_item
from app.fsm_groups.fsm import UpdateItemFSM
from aiogram.fsm.context import FSMContext
from aiogram.filters import or_f


change_price_router = Router()


@change_price_router.callback_query(F.data == 'edit_item')
async def choose_action(callback: CallbackQuery):
    await callback.message.edit_caption(caption='Оберіть дію',
                                        reply_markup=kb.action)


@change_price_router.callback_query(or_f(F.data == 'edit_item_price', F.data == 'edit_item_name',
                                         F.data == 'edit_item_description'))
async def get_all_games(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    await state.set_state(UpdateItemFSM.action)
    await state.update_data(action=action.removeprefix('edit_'))
    await callback.message.edit_caption(text='Оберіть ігрову категорію',
                                        reply_markup=await kb.game_categories(prefix='pricegame'))


@change_price_router.callback_query(F.data.startswith('pricegame_'))
async def get_ingame_categories(callback: CallbackQuery):
    game_category = callback.data.split('_')
    game_category_id = int(game_category[3])
    await callback.message.edit_caption(text='Оберіть підкатегорію',
                                        reply_markup=await kb.category_items(category_id=game_category_id,
                                                                             prefix='special'))


@change_price_router.callback_query(F.data.startswith('special'))
async def gat_all_items(callback: CallbackQuery):
    data = callback.data.split('_')
    ingame_category_id = int(data[1])
    await callback.message.edit_caption(caption='Оберіть товар для редагування',
                                        reply_markup=await kb.get_items_names(category_id=ingame_category_id,
                                                                              prefix='newprice'))


@change_price_router.callback_query(F.data.startswith('newprice'))
async def update_item(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split('_')
    item_id = int(data[1])
    item_name = data[2]
    await state.update_data(item_id=item_id, item_name=item_name)
    action = await state.get_data()
    if action['action'] == 'item_price':
        await state.set_state(UpdateItemFSM.new_price)
        await callback.message.answer(text='Впишіть нову ціну у числовому форматі')
    elif action['action'] == 'item_name':
        await state.set_state(UpdateItemFSM.new_name)
        await callback.message.answer(text='Впишіть нову назву з великої літери')
    else:
        await state.set_state(UpdateItemFSM.new_desc)
        await callback.message.answer(text='Впишіть новий опис для товару')


@change_price_router.message(F.text, UpdateItemFSM.new_price)
async def set_new_price(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(new_price=message.text)
        data = await state.get_data()
        item_id = data['item_id']
        item_name = data['item_name']
        new_price = int(data['new_price'])
        if await edit_item(item_id=item_id, edit_selector=new_price, prefix='item_price'):
            await state.clear()
            await message.answer(text=f"Ціна на товар '{item_name}' оновлена")


@change_price_router.message(F.text, UpdateItemFSM.new_name)
async def set_new_name(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(new_name=message.text)
        data = await state.get_data()
        item_id = data['item_id']
        item_name = data['item_name']
        new_name = data['new_name']
        if await edit_item(item_id=item_id, edit_selector=new_name, prefix='item_name'):
            await state.clear()
            await message.answer(text=f"Назва товару {item_name} змінена на {new_name}")


@change_price_router.message(F.text, UpdateItemFSM.new_desc)
async def set_new_desc(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(new_desc=message.text)
        data = await state.get_data()
        item_id = data['item_id']
        item_name = data['item_name']
        new_desc = data['new_desc']
        if await edit_item(item_id=item_id, edit_selector=new_desc, prefix='item_description'):
            await state.clear()
            await message.answer(text=f"Опис {item_name} змінений на {new_desc}")
