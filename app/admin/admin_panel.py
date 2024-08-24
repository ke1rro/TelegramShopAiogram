from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery


import app.keyboards.admin_panel_kb as kb
from app.utils.check_admin import AdminChecker
from app.admin.create_products import create_products_router
from app.admin.export_users import export_users_router
from app.admin.delete_products import delete_products_router
from app.admin.change_item_price import change_price_router
from app.admin.export_orders import export_orders_router
from app.admin.edit_photos import edit_photo_router

ADMIN_PANEL = 'img/Admin_panel.jpg'
admin_panel_photo = FSInputFile(ADMIN_PANEL)

admin_panel_router = Router()
admin_panel_router.include_router(create_products_router)
admin_panel_router.include_router(export_users_router)
admin_panel_router.include_router(export_orders_router)
admin_panel_router.include_router(change_price_router)
admin_panel_router.include_router(delete_products_router)
admin_panel_router.include_router(edit_photo_router)


@admin_panel_router.message(Command('admin_panel'), AdminChecker())
async def get_admin_panel(message: Message, bot: Bot):
    await bot.send_photo(message.from_user.id, photo=admin_panel_photo,
                         caption='Ви увійшли до адмін панелі оберіть дію',
                         reply_markup=kb.admin_commands)


@admin_panel_router.callback_query(F.data == 'admin_back')
async def get_back_to_admin(callback: CallbackQuery, bot: Bot):
    await bot.edit_message_caption(chat_id=callback.from_user.id,
                                   message_id=callback.message.message_id,
                                   caption='Ви увійшли до адмін панелі оберіть дію',
                                   reply_markup=kb.admin_commands)
