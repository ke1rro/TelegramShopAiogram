import app.fsm_groups.fsm as fsm
from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import app.keyboards.admin_create_kb as admin_create_kb
from app.database.requests_db.add_item_request import add_product_with_photo
from app.google_drive.google_cdn import upload_photo

create_products_router = Router()

@create_products_router.callback_query(F.data == 'create_product')
async def add_product(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        text='Оберіть наявну ігрову категорію або впишіть свою з великої літери',
        reply_markup=await admin_create_kb.game_categories()
    )
    await callback.answer()
    await state.set_state(fsm.AddItem.game_category)


@create_products_router.callback_query(F.data.startswith('game_'), fsm.AddItem.game_category)
async def select_game_category(callback: CallbackQuery, state: FSMContext):
    game_callback = callback.data.split('_')
    game_category = game_callback[1]
    game_id = game_callback[2]
    await callback.message.answer(
        text=f'Ви обрали категорію: {game_category}\nID категорії: {game_id}'
    )
    await state.update_data(game_category=game_category, game_category_id=game_id, skip_game=True)
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.set_state(fsm.AddItem.category_item_name)
    await callback.message.answer(
        text='Оберіть підкатегорію або впишіть свою з великої літери',
        reply_markup=await admin_create_kb.category_items(game_id)
    )


@create_products_router.message(fsm.AddItem.game_category)
async def select_game_category_text(message: Message, state: FSMContext):
    game_name = message.text
    await state.update_data(game_category=game_name, skip_game=False)
    await state.set_state(fsm.AddItem.category_item_name)
    await message.answer(text='Ви додали нову ігрову категорію, тепер додайте підкатегорію')


@create_products_router.callback_query(F.data.startswith('ingame_'), fsm.AddItem.category_item_name)
async def select_ingame_category(callback: CallbackQuery, state: FSMContext):
    ingame_callback = callback.data.split('_')
    ingame_category_id = int(ingame_callback[1])
    ingame_category_name = ingame_callback[2]
    ingame_game_category = int(ingame_callback[3])
    text = f'Ви обрали підкатегорію: {ingame_category_name}\n' \
           f'ID підкатегорії: {ingame_category_id}\n' \
           f'ID ігрова Категорія: {ingame_game_category}'
    await callback.message.answer(text)
    await state.update_data(category_item_name=ingame_category_name, category_item_id=ingame_category_id, skip_ingame=True)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text='Додайте назву товару для продажу')
    await state.set_state(fsm.AddItem.item_name)


@create_products_router.message(fsm.AddItem.category_item_name)
async def select_ingame_category_text(message: Message, state: FSMContext):
    ingame_category_name = message.text
    await state.update_data(category_item_name=ingame_category_name, skip_ingame=False)
    await state.set_state(fsm.AddItem.item_name)
    await message.answer(text='Ви додали нову підкатегорію, тепер додайте назву товару для продажу')


@create_products_router.message(fsm.AddItem.item_name)
async def add_item_name(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(item_name=message.text)
    await bot.send_message(
        message.from_user.id,
        text='Назву для товару додано, додайте ціну',
        reply_markup=admin_create_kb.cancel_markup
    )
    await state.set_state(fsm.AddItem.item_price)


@create_products_router.message(fsm.AddItem.item_price)
async def add_item_price(message: Message, state: FSMContext, bot: Bot):
    if message.text.isdigit():
        await state.update_data(item_price=int(message.text))
        await bot.send_message(
            message.from_user.id,
            text='Ціну для товару додано, додайте опис',
            reply_markup=admin_create_kb.cancel_markup
        )
        await state.set_state(fsm.AddItem.item_description)
    else:
        await bot.send_message(
            message.from_user.id,
            text='Будь ласка впишіть дані в числовому форматі'
        )


@create_products_router.message(fsm.AddItem.item_description)
async def add_item_description(message: Message, state: FSMContext, bot: Bot):
    item_description = message.text
    data = await state.get_data()
    await state.update_data(item_description=item_description)
    if data['skip_game'] is True and data['skip_ingame'] is True:
        await bot.send_message(chat_id=message.from_user.id, text='Додайте фото для товару',
                               reply_markup=admin_create_kb.cancel_markup)
        await state.update_data(game_photo=None, ingame_photo=None,
                                proceed_ingame_photo=None, proceed_game_photo=None)
        await state.set_state(fsm.AddItem.item_photo_id)

    elif data['skip_game'] is True:
        await bot.send_message(chat_id=message.from_user.id, text='Додайте фото для підкатегорії',
                               reply_markup=admin_create_kb.set_ingame_photo_kb)
        await state.update_data(game_photo=None, proceed_game_photo=None)
        await state.set_state(fsm.AddItem.ingame_photo)

    else:
        await bot.send_message(
            message.from_user.id,
            text='Опис додано, додайте фото для ігрової категорії, або залиште стандратне',
            reply_markup=admin_create_kb.set_game_photo_kb
        )
        await state.set_state(fsm.AddItem.game_photo)


@create_products_router.callback_query(F.data == 'defaultgame', fsm.AddItem.game_photo)
async def get_game_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await state.update_data(game_photo='Shop')
    await state.update_data(proceed_game_photo=None)
    await state.set_state(fsm.AddItem.ingame_photo)
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Встановлено стандранте зображення! Тепер додайте фото підкатегорії',
                           reply_markup=admin_create_kb.set_ingame_photo_kb)


@create_products_router.callback_query(F.data == '1set_game', fsm.AddItem.game_photo)
async def game_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await state.set_state(fsm.AddItem.proceed_game_photo)
    await bot.send_message(chat_id=callback.from_user.id, text='Відправте фото для ігової категорії')


@create_products_router.message(F.photo, fsm.AddItem.proceed_game_photo)
async def set_game_photo(message: Message, bot: Bot, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await message.bot.download(file=message.photo[-1].file_id, destination=f'app/bot_imgs/{photo_id}.jpg')
    await state.set_state(fsm.AddItem.ingame_photo)
    await bot.send_message(chat_id=message.from_user.id, text='Фото збережено! Тепер оберіть фото для підкатегорії',
                           reply_markup=admin_create_kb.set_ingame_photo_kb)
    await state.update_data(proceed_game_photo=photo_id)
    await state.update_data(game_photo=None)


@create_products_router.callback_query(F.data == 'defaultingame', fsm.AddItem.ingame_photo)
async def get_ingame_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await state.update_data(ingame_photo='Shop')
    await state.update_data(proceed_ingame_photo=None)
    await state.set_state(fsm.AddItem.item_photo_id)
    await bot.send_message(chat_id=callback.from_user.id,
                           text='Встановлено стандранте зображення! Тепер додайте фото товару')


@create_products_router.callback_query(F.data == '2set_ingame', fsm.AddItem.ingame_photo)
async def ingame_photo(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer()
    await state.set_state(fsm.AddItem.proceed_ingame_photo)
    await bot.send_message(chat_id=callback.from_user.id, text='Відправте фото для підкатегорії')


@create_products_router.message(F.photo, fsm.AddItem.proceed_ingame_photo)
async def set_game_photo(message: Message, bot: Bot, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.set_state(fsm.AddItem.item_photo_id)
    await message.bot.download(file=message.photo[-1].file_id, destination=f'app/bot_imgs/{photo_id}.jpg')
    await bot.send_message(chat_id=message.from_user.id, text='Фото збережено! Тепер оберіть фото для торвару',
                           reply_markup=admin_create_kb.cancel_markup)
    await state.update_data(proceed_ingame_photo=photo_id)
    await state.update_data(ingame_photo=None)


@create_products_router.message(fsm.AddItem.item_photo_id)
async def add_item_photo(message: Message, state: FSMContext, bot: Bot):
    if message.photo:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file_info.file_path)
        photo_name = f"{photo.file_id}.jpg"
        photo_id_db = await upload_photo(photo_bytes.read(), photo_name)

        if photo_id_db:
            await state.update_data(item_photo_id=photo_id_db)
            item_data = await state.get_data()
            await add_product_with_photo(item_data)
            await bot.send_message(message.from_user.id, text='Товар успішно додано')
            await state.clear()
        else:
            await bot.send_message(message.from_user.id, text='Не вдалося завантажити фото, спробуйте ще раз')
    else:
        text = 'Будь ласка, надішліть фото, а не будь-який інший формат повідомлення'
        await bot.send_message(message.from_user.id, text=text)


@create_products_router.callback_query(F.data == 'cancel')
async def cancel_adding(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.clear()
    await callback.message.delete()
    await bot.send_message(callback.from_user.id, text='Дія відмінена')
    await callback.answer()
