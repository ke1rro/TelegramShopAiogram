
from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.enums import ParseMode
import app.keyboards.main_menu_kb as kb


guarantees_router = Router()
GUARANTEES_PATH = 'img/guarantees.jpg'
guarantees = FSInputFile(GUARANTEES_PATH)


@guarantees_router.callback_query(F.data == 'guarantees')
async def get_guarantees(callback: CallbackQuery):
    content = 'Щоб ознайомитись із гарантіями, натисни – <b><a href="https://telegra.ph/Garant%D1%96i-v%D1%96d-magazinu-06-30">тут</a></b>'
    await callback.message.delete()
    await callback.message.answer_photo(photo=guarantees, caption=content, reply_markup=kb.back_button, parse_mode=ParseMode.HTML)
