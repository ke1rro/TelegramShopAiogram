import re
import os
from dotenv import load_dotenv

import app.database.requests_db.user_requests as user_req
import app.fsm_groups.fsm as fsm
import app.keyboards.main_menu_kb as kb
import app.database.requests_db.requests as request

from app.database.requests_db.request_by_card import new_order_card, check_order
from app.middleware.subscription_and_reg_check import ChannelSubscribeMiddleware
from app.utils.id_generator import order_id
from app.middleware.antiflood import ThrottlingMiddleware
from app.cache.redis_cache import redis
from app.logger.log_maker import logger
from app.database.requests_db.photo_req import get_game_photo, get_ingame_photo

from aiogram import F, Router, Bot
from aiogram.filters import CommandStart
from app.google_drive.google_cdn import get_file_url
from aiogram.fsm.context import FSMContext
from aiogram.types import (Message,
                           CallbackQuery,
                           FSInputFile,
                           InputMediaPhoto,
                           ReplyKeyboardRemove)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


router = Router()
load_dotenv()
HOKAGE_SHOP_PATH = 'img/HokageShop.jpg'
SHOP_MEDIA_PATH = 'img/Shop.jpg'
fortnite = FSInputFile(HOKAGE_SHOP_PATH)
shop_media = FSInputFile(SHOP_MEDIA_PATH)
POST_CHANNEL = os.getenv('POST_CHANNEL')
PAYMENT_CHANNEL = os.getenv('PAYMENT_CHANNEL')
router.message.middleware(ChannelSubscribeMiddleware(chat_ids=[POST_CHANNEL]))
router.callback_query.middleware(ChannelSubscribeMiddleware(chat_ids=[POST_CHANNEL]))
router.message.middleware(ThrottlingMiddleware(redis_storage=redis))


@router.message(CommandStart())
async def check_sub(message: Message):
    await message.answer_photo(photo=fortnite, caption='Головне меню', reply_markup=kb.main_menu)


@router.callback_query(F.data == 'check_sub')
async def handle_check_sub(callback: CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer_photo(photo=fortnite, caption='Головне меню', reply_markup=kb.main_menu)


@router.message(F.contact, fsm.Registration.phone_number)
async def phone_number_handler(message: Message, state: FSMContext):
    contact = message.contact
    await user_req.update_user_phone_number(telegram_id=contact.user_id, phone_number=contact.phone_number)

    await message.answer(text='Зареєстровано!',
                         reply_markup=ReplyKeyboardRemove())
    await state.clear()
    await message.answer_photo(photo=fortnite,
                               caption='Головне меню',
                               reply_markup=kb.main_menu)


@router.callback_query(F.data == 'shop')
async def open_catalog(callback: CallbackQuery):
    await callback.message.edit_media(media=InputMediaPhoto(media=shop_media),
                                      caption=' ',
                                      reply_markup=await kb.game_categories())


@router.callback_query(F.data.startswith('category_'))
async def open_game_catalog(callback: CallbackQuery):
    game_id = callback.data.split('_')[1]
    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'app/bot_imgs/{await get_game_photo(game_id)}')),
                                      caption='Оберіть категорію',
                                      reply_markup=await kb.category_items(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('Ingameitem_'))
async def ingame_items_names(callback: CallbackQuery):
    data_parts = callback.data.split('_')
    category_id = data_parts[1]
    items_markup = await kb.get_items_names(category_id)
    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'app/bot_imgs/{await get_ingame_photo(category_id)}')),
                                      caption='Оберіть товар',
                                      reply_markup=items_markup)


@router.callback_query(F.data.startswith('item_'))
async def item_callback_handler(callback: CallbackQuery):
    data_parts = callback.data.split('_')
    item_id = data_parts[2]
    item_details = await request.get_item_details_by_id(item_id)
    item_photo_google_id = await request.get_item_photo_by_id(item_id=int(item_id))
    photo_url = await get_file_url(photo_name=item_photo_google_id)
    if item_details:
        creat_invoice_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Сформувати замовлення', callback_data=f'INVOICE_{item_details.item_id}_{item_details.item_price}_{item_details.item_name}')],
                                                                 [InlineKeyboardButton(text='Назад', callback_data=f'Ingameitem_{item_details.category_item_id}')]])
        details_message = f"Товар: {item_details.item_name}\nЦіна: {item_details.item_price}₴\n\nОпис: {item_details.item_description}"
        await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=details_message), reply_markup=creat_invoice_kb)
    else:
        await callback.message.edit_caption(caption="Помилка! Товар не знайдено.", reply_markup=kb.back_button)


@router.callback_query(F.data.startswith('INVOICE_'))
async def payment_method(callback: CallbackQuery):
    item_data = callback.data
    link_pay = 'L' + item_data
    card_pay = 'C' + item_data
    await callback.answer()
    payment_methods = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Переказ на карту', callback_data=card_pay)],
        [InlineKeyboardButton(text='Плітжне посилання', callback_data=link_pay)]])
    await callback.message.answer(text='Оберіть метод для оплати', reply_markup=payment_methods)


@router.callback_query(F.data.startswith('CINVOICE_'))
async def card_payment(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    await callback.message.delete()
    item_details = callback.data.split('_')
    item_id = item_details[1]
    item_price = item_details[2]
    item_name = item_details[3]
    username = callback.from_user.username
    current_order_id = order_id()
    user_phone_num = await user_req.get_phone_num_invoice(telegram_id=callback.from_user.id)
    await state.update_data(item_id=item_id, item_name=item_name,
                            item_price=item_price, user_phone_num=user_phone_num,
                            telegram_id=callback.from_user.id, order_id=current_order_id,
                            username=username)
    order_details = f'Ваше замовлення: # {current_order_id}\nТовар: {item_name}\nЦіна: {item_price}₴\nПереказ на карут ХХХХХХХХХХХ на суму {item_price}, після переказу надішліть зміномок екрану про успішну оплату у чат з ботом і очікуйте підтведження\n\nОБОВ`ЯЗКОВО у підписі до фото надішліть номер замовлення, замовлення без підпису не будуть оброблятись'
    await state.set_state(fsm.ProceedPayment.photo)
    await bot.send_message(chat_id=callback.from_user.id, text=order_details, reply_markup=kb.cancel_order)


@router.message(F.photo, fsm.ProceedPayment.photo)
async def get_payment_screen(message: Message, state: FSMContext, bot: Bot):
    item_data = await state.get_data()
    if message.photo:
        if item_data['order_id'] not in message.caption:
            await bot.send_message(chat_id=message.from_user.id, text='В підписі до фото немає номеру замовлення')
        else:
            try:
                new_order = await new_order_card(telegram_id=int(item_data['telegram_id']),
                                                 order_id=item_data['order_id'],
                                                 customer_name=message.from_user.first_name,
                                                 customer_phone=await user_req.get_phone_num_invoice(telegram_id=int(message.from_user.id)),
                                                 item_name=item_data['item_name'], item_price=int(item_data['item_price']))
                if new_order:
                    forwarded_message = await bot.send_photo(chat_id=PAYMENT_CHANNEL, photo=message.photo[-1].file_id,
                                                             caption=f'Нове замовлення # {item_data['order_id']}\nТовар: {item_data['item_name']}\nЦіна: {item_data['item_price']}₴\nКористувач: {item_data['username']}\nID користувача: {item_data['telegram_id']}\nНомер телефону: {item_data['user_phone_num']}')
                    logger.info(f'Payment Photo Sent {new_order.order_id} USER ID: {new_order.customer_tg_id}')
                    await state.clear()
            except Exception as e:
                logger.error(e)


@router.callback_query(F.data.startswith('LINVOICE_'))
async def accept_invoice(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await bot.send_message(chat_id=callback.from_user.id, text='Наразі цей метод оплати не працює')


@router.channel_post(F.reply_to_message)
async def handle_channel_reply(message: Message, bot: Bot):
    if message.reply_to_message and message.reply_to_message.caption:
        message_text = message.reply_to_message.caption
        order_id_match = re.search(r'замовлення # (\S+)', message_text)
        order_id = order_id_match.group(1) if order_id_match else None

        user_id_match = re.search(r'ID користувача: (\d+)', message_text)
        user_id = user_id_match.group(1) if user_id_match else None
        telegeram_id = await check_order(telegram_id=int(user_id), order_id=order_id)
        if telegeram_id:
            await bot.send_message(chat_id=telegeram_id, text='Ваше замовлення!')
            await bot.send_message(chat_id=telegeram_id, text=message.text)


@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery):
    await callback.message.edit_media(media=InputMediaPhoto(media=fortnite),
                                      reply_markup=kb.main_menu)


@router.callback_query(F.data == 'back_to_game_categories')
async def back_to_game_categories(callback: CallbackQuery):
    await callback.message.edit_media(media=InputMediaPhoto(media=shop_media),
                                      reply_markup=await kb.game_categories())


@router.callback_query(F.data.startswith('back_to_category_'))
async def back_to_category(callback: CallbackQuery):
    category_id = callback.data.split('_')[4]
    game_id = callback.data.split('_')[3]
    await callback.message.edit_media(media=InputMediaPhoto(media=FSInputFile(f'app/bot_imgs/{await get_game_photo(category_id)}')),
                                      reply_markup=await kb.category_items(int(category_id)))


@router.callback_query(F.data == 'ORDCANCEL')
async def cancel_order_status(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(chat_id=callback.from_user.id, text='Замовлення скасоване')
    await callback.message.delete()
    await callback.answer()
    await state.clear()
