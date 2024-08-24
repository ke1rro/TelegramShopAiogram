from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    phone_number = State()
    first_name = State()
    telegram_id = State()


class AddItem(StatesGroup):
    game_category = State()
    game_category_id = State()
    category_item_name = State()
    category_item_id = State()
    item_name = State()
    item_price = State()
    item_description = State()
    item_photo_id = State()
    game_photo = State()
    proceed_game_photo = State()
    ingame_photo = State()
    proceed_ingame_photo = State()
    skip_game = State()
    skip_ingame = State()


class UpdateItemFSM(StatesGroup):
    new_price = State()
    item_name = State()
    new_name = State()
    new_desc = State()
    item_id = State()
    action = State()


class ProceedPayment(StatesGroup):
    item_id = State()
    item_name = State()
    item_price = State()
    user_phone_num = State()
    username = State()
    telegram_id = State()
    order_id = State()
    photo = State()


class EditPhoto(StatesGroup):
    game_category = State()
    ingame_category = State()
    item_id = State()
    old_photo = State()
    new_photo = State()
    new_ingame_photo = State()
    new_item_photo = State()
