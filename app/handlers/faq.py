from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.enums import ParseMode
import app.keyboards.main_menu_kb as kb
faq_router = Router()


@faq_router.callback_query(F.data == 'FAQ')
async def get_faq(callback: CallbackQuery):
    content = 'Відповіді на часто задавані питання можна знайти <b><a href="https://telegra.ph/V%D1%96dpov%D1%96d%D1%96-na-pitannya-06-30">тут</a></b>'
    await callback.message.edit_caption(caption=content, reply_markup=kb.back_button, parse_mode=ParseMode.HTML)
