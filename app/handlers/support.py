from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
import app.keyboards.main_menu_kb as kb

support_router = Router()


@support_router.callback_query(F.data == 'support')
async def get_support(callback: CallbackQuery):
    content = 'Якщо у вас є додаткові питання або пропозиції, звертайтесь в особисті повідомлення до менеджера <b><a href="https://t.me/rnija">тут</a></b>'
    await callback.message.edit_caption(caption=content, reply_markup=kb.back_button, parse_mode=ParseMode.HTML)
