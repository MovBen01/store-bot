import asyncio
import logging
import sys
import os

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, WEBAPP_URL
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


async def run_bot():
    await init_db()
    logger.info("Database initialized")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    provider = MockProvider()
    calc = PriceCalculator(provider)
    dp["price_calc"] = calc
    dp["webapp_url"] = WEBAPP_URL

    dp.include_router(admin_router)
    dp.include_router(user_router)

    logger.info("Starting bot...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


async def run_api():
    from api.server import app
    port = int(os.environ.get("PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    await asyncio.gather(run_bot(), run_api())


if __name__ == "__main__":
    asyncio.run(main())
