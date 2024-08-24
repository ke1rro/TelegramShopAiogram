import app.keyboards.main_menu_kb as kb


from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile


profile_router = Router()
PROFILE_PATH = 'img/profile.jpg'
profile = FSInputFile(PROFILE_PATH)


@profile_router.callback_query(F.data == 'account')
async def get_user_account(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id is not None:
        await callback.message.delete()
        user_info = f'Ваш профіль \nID профілю {callback.from_user.id}'
        await callback.message.answer_photo(photo=profile, caption=user_info, reply_markup=kb.back_button)
    else:
        await callback.message.answer(text='Користувач не знайдений')
