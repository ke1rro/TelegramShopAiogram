import os
import asyncio


from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from app.handlers.faq import faq_router
from app.handlers.handlers import router
from app.handlers.support import support_router
from app.handlers.reviews import reviews_router
from app.database.models import init_models, SessionLocal
from app.utils.commands import set_commands
from app.handlers.guarantees import guarantees_router
from app.admin.admin_panel import admin_panel_router
from app.cache.redis_cache import redis
from app.handlers.profile import profile_router
from app.logger.log_maker import logger


async def main() -> None:
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(token=TOKEN)
    await init_models()
    dp = Dispatcher(storage=RedisStorage(redis=redis, state_ttl=300, data_ttl=600))
    dp.include_router(router)
    dp.include_router(faq_router)
    dp.include_router(profile_router)
    dp.include_router(reviews_router)
    dp.include_router(support_router)
    dp.include_router(guarantees_router)
    dp.include_router(admin_panel_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await set_commands(bot)
    await dp.start_polling(bot, session=SessionLocal, skip_updates=True)


if __name__ == "__main__":
    try:
        logger.info("Starting bot")
        print('Starting bot...')
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
        print('Exit')
