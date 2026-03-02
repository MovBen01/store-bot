import logging
from telegram.ext import ApplicationBuilder

from config import BOT_TOKEN
from database.db import init_db
from handlers.start import get_start_handlers
from handlers.catalog import get_catalog_handlers
from handlers.cart import get_cart_handlers
from handlers.orders import get_orders_handlers
from handlers.search import get_search_handlers
from handlers.admin import get_admin_handlers

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не задан! Укажите его в файле .env")
        return

    init_db()
    logger.info("База данных инициализирована.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    for handler in get_admin_handlers():
        app.add_handler(handler)

    for handler in get_search_handlers():
        app.add_handler(handler)

    for handler in get_cart_handlers():
        app.add_handler(handler)

    for handler in get_catalog_handlers():
        app.add_handler(handler)

    for handler in get_orders_handlers():
        app.add_handler(handler)

    for handler in get_start_handlers():
        app.add_handler(handler)

    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
