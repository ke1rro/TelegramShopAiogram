from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.keyboards.admin_edit_photos_kb import photo_action, game_categories, category_items, get_items_names
from app.fsm_groups import fsm
from app.database.requests_db.photo_req import (get_old_gm_photo,
                                                get_old_ingm_photo,
                                                get_old_item_photo,
                                                replace_old_gm_photo,
                                                replace_olg_ingm_photo,
                                                replace_old_item_photo)
from app.google_drive.google_cdn import upload_photo


edit_photo_router = Router()


@edit_photo_router.callback_query(F.data == 'EDIT_photos')
async def choose_action_ph(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await bot.send_message(chat_id=callback.from_user.id, text='Оберіть опцію для зміни фото', reply_markup=photo_action)


@edit_photo_router.callback_query(F.data == 'gmphoto')
async def choose_game_category(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await bot.send_message(chat_id=callback.from_user.id, text='Оберіть ігорву категорію',
                           reply_markup=await game_categories('GAMEphoto'))
    await state.set_state(fsm.EditPhoto.game_category)


@edit_photo_router.callback_query(F.data.startswith('GAMEphoto'), fsm.EditPhoto.game_category)
async def get_new_gm_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):
    game_id = callback.data.split('_')[3]
    await callback.answer()
    old_photo = await get_old_gm_photo(game_id)
    await state.update_data(game_category=game_id, ingame_category=None, item_id=None, old_photo=old_photo)
    await bot.send_message(chat_id=callback.from_user.id, text='Відправте нове фото')
    await state.set_state(fsm.EditPhoto.new_photo)


@edit_photo_router.message(F.photo, fsm.EditPhoto.new_photo)
async def proceed_photo(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    new_photo = message.photo[-1].file_id
    data = await state.get_data()
    game_id = data['game_category']
    await message.bot.download(file=message.photo[-1].file_id, destination=f'app/bot_imgs/{new_photo}.jpg')
    if await replace_old_gm_photo(game_category_id=game_id, new_photo_id=new_photo):
        await bot.send_message(chat_id=message.from_user.id, text='Фото оновлено')
        await state.clear()


@edit_photo_router.callback_query(F.data == 'ingphoto')
async def game_category(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await bot.send_message(chat_id=callback.from_user.id, text='Оберіть ігрову категорію', reply_markup=await game_categories(prefix='INGAMESTEP1'))
    await state.set_state(fsm.EditPhoto.game_category)


@edit_photo_router.callback_query(F.data.startswith('INGAMESTEP1_'), fsm.EditPhoto.game_category)
async def ingame_category(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    data = callback.data.split('_')
    game_id = data[3]
    await bot.send_message(chat_id=callback.from_user.id, text='Оберіть підкатегорію',
                           reply_markup=await category_items(category_id=game_id, prefix='INGAMESTEP2'))
    await state.update_data(item_id=None, game_category=game_id)
    await state.set_state(fsm.EditPhoto.old_photo)


@edit_photo_router.callback_query(F.data.startswith('INGAMESTEP2_'), fsm.EditPhoto.old_photo)
async def get_ingame_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await bot.send_message(chat_id=callback.from_user.id, text='Відправте нове фото!')
    data = await state.get_data()
    category_id = callback.data.split('_')[1]
    game_id = data['game_category']
    old_photo = await get_old_ingm_photo(category_id=category_id, game_category_id=game_id)
    await state.update_data(old_photo=old_photo, ingame_category=category_id)
    await state.set_state(fsm.EditPhoto.new_ingame_photo)


@edit_photo_router.message(F.photo, fsm.EditPhoto.new_ingame_photo)
async def proceed_ingame_photo(message: Message, state: FSMContext, bot: Bot):
    new_photo = message.photo[-1].file_id
    data = await state.get_data()
    ingame_category_id = data['ingame_category']
    if await replace_olg_ingm_photo(category_id=ingame_category_id, new_photo_id=new_photo):
        await message.bot.download(file=message.photo[-1].file_id, destination=f'app/bot_imgs/{new_photo}.jpg')
        await bot.send_message(chat_id=message.from_user.id, text='Фото оновлено')
        await state.clear()


@edit_photo_router.callback_query(F.data == 'itemphoto')
async def get_games_for_item(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await bot.send_message(chat_id=callback.from_user.id, text='Оберіть ігрову категорію',
                           reply_markup=await game_categories(prefix='ITEMSTEP1'))
    await state.set_state(fsm.EditPhoto.game_category)


@edit_photo_router.callback_query(F.data.startswith('ITEMSTEP1_'), fsm.EditPhoto.game_category)
async def get_game_names_item(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    game_id = callback.data.split('_')[3]
    await state.update_data(game_category=game_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Оберіть підкатегорію',
                           reply_markup=await category_items(category_id=game_id, prefix='ITEMSTEP2'))
    await state.set_state(fsm.EditPhoto.ingame_category)


@edit_photo_router.callback_query(F.data.startswith('ITEMSTEP2_'), fsm.EditPhoto.ingame_category)
async def get_item_names(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    ingame_id = callback.data.split('_')[1]
    await state.update_data(ingame_category=ingame_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Оберіть товар, для зміни фото',
                           reply_markup=await get_items_names(category_id=int(ingame_id), prefix='ITEMSTEP3'))
    await state.set_state(fsm.EditPhoto.old_photo)


@edit_photo_router.callback_query(F.data.startswith('ITEMSTEP3_'), fsm.EditPhoto.old_photo)
async def get_old_photo_item(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    item_id = callback.data.split('_')[1]
    data = await state.get_data()
    old_photo = await get_old_item_photo(game_category_id=data['game_category'],
                                         category_id=data['ingame_category'],
                                         item_id=item_id)
    await bot.send_message(chat_id=callback.from_user.id, text='Відравте фото')
    await state.update_data(old_photo=old_photo, item_id=item_id)
    await state.set_state(fsm.EditPhoto.new_item_photo)


@edit_photo_router.message(F.photo, fsm.EditPhoto.new_item_photo)
async def proceed_item_photo(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    category_id = data['ingame_category']
    item_id = data['item_id']
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file_info.file_path)
    photo_name = f"{photo.file_id}.jpg"
    photo_id_db = await upload_photo(photo_bytes.read(), photo_name)
    if await replace_old_item_photo( category_id=category_id, item_id=item_id, new_photo=photo_id_db):
        await bot.send_message(chat_id=message.from_user.id, text='Фото оновлено')
        await state.clear()
