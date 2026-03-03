import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from bot.db import init_db
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router
from bot.services.pricing import MockProvider, PriceCalculator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    await init_db()
    logger.info("Database initialized")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Init price calculator and store in bot data
    provider = MockProvider()
    calc = PriceCalculator(provider)
    dp["price_calc"] = calc

    dp.include_router(admin_router)
    dp.include_router(user_router)

    logger.info("Starting bot...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
