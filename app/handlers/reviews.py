from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
import app.keyboards.main_menu_kb as kb

reviews_router = Router()


@reviews_router.callback_query(F.data == 'reviews')
async def get_reviews(callback: CallbackQuery):
    content = 'Канал з відгуками задоволених покупців <b><a href="https://t.me/otzuvskinchiki">тут</a></b>'
    await callback.message.edit_caption(caption=content, reply_markup=kb.back_button, parse_mode=ParseMode.HTML)
