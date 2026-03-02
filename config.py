import os
from dotenv import load_dotenv

load_dotenv()

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
