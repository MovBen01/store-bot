import os
from dotenv import load_dotenv

load_dotenv()

<<<<<<< HEAD
BOT_TOKEN: str = os.environ["BOT_TOKEN"]
ADMIN_IDS: list[int] = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
PRICE_PROVIDER: str = os.getenv("PRICE_PROVIDER", "mock")
MARKUP_MODE: str = os.getenv("MARKUP_MODE", "percent")
MARKUP_VALUE: float = float(os.getenv("MARKUP_VALUE", "10"))
DB_PATH: str = os.getenv("DB_PATH", "shop.db")

USERBOT_API_ID: str = os.getenv("USERBOT_API_ID", "")
USERBOT_API_HASH: str = os.getenv("USERBOT_API_HASH", "")
USERBOT_SESSION: str = os.getenv("USERBOT_SESSION", "userbot_session")
BIGSALE_BOT_USERNAME: str = os.getenv("BIGSALE_BOT_USERNAME", "BigSaleApple")
=======
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()
]

DB_PATH = "store.db"

ITEMS_PER_PAGE = 5
PRODUCTS_PER_PAGE = 4

CURRENCY = "₽"

STATUSES = {
    "pending":    "⏳ Ожидает подтверждения",
    "confirmed":  "✅ Подтверждён",
    "processing": "🔧 В обработке",
    "shipped":    "🚚 Отправлен",
    "delivered":  "📦 Доставлен",
    "cancelled":  "❌ Отменён",
}
>>>>>>> a3f6ff9e60154a5b9e6d149779d7bbcc564473b9
