from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery
from typing import Callable, Any, Awaitable
from app.database.requests_db.user_requests import check_user, check_phone_number
from app.keyboards import main_menu_kb as kb
from aiogram.fsm.storage.base import StorageKey
from app.database.requests_db.user_requests import registrate_user
from app.fsm_groups.fsm import Registration
from aiogram.exceptions import TelegramNotFound
from aiogram.methods import GetChatMember
from aiogram.enums import ChatMemberStatus


class ChannelSubscribeMiddleware(BaseMiddleware):

    def __init__(self, chat_ids: list[int | str] | int | str) -> None:
        self.chat_ids = chat_ids
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        message: Message = event

        if not message.from_user:
            return await handler(event, data)

        session = data['session']
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        storage = data['dispatcher'].storage
        bot: Bot = data["bot"]
        user_auth = await check_user(session, user_id)
        user_phone_num = await check_phone_number(user_id)

        if await self._is_subscribed(bot=bot, user_id=user_id) and user_auth is True and user_phone_num is True:
            return await handler(event, data)
        else:
            if isinstance(event, CallbackQuery):
                await message.bot.delete_message(chat_id=user_id, message_id=event.message.message_id)
            if await self._is_subscribed(bot=bot, user_id=user_id) is False:
                await message.bot.send_message(chat_id=user_id,
                                               text='Для того аби користуватись ботом підпишіться на канал',
                                               reply_markup=kb.check_subscription)
                return None
            if user_phone_num is None or user_phone_num is False:
                try:
                    if message.contact and await self._is_subscribed(bot=bot, user_id=user_id) is True:
                        return await handler(event, data)
                except AttributeError:
                    pass
                key = StorageKey(chat_id=user_id, user_id=event.from_user.id, bot_id=event.bot.id)
                await storage.set_state(key=key, state=Registration.phone_number.state)
                await registrate_user(username=username, telegram_id=user_id, first_name=first_name)
                await message.bot.send_message(chat_id=user_id,
                                               text='Поділіться номером телефону для того аби продовжити',
                                               reply_markup=kb.phone_num_request)
                return None
            return None

    async def _is_subscribed(self, bot: Bot, user_id: int) -> bool:
        if isinstance(self.chat_ids, list):
            for chat_id in self.chat_ids:
                try:
                    member = await bot(GetChatMember(chat_id=chat_id, user_id=user_id))
                except TelegramNotFound:
                    return False

                if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED):
                    return False

        elif isinstance(self.chat_ids, (str, int)):
            try:
                member = await bot(GetChatMember(chat_id=self.chat_ids, user_id=user_id))
            except TelegramNotFound:
                return False

            if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
                return False

        return True
