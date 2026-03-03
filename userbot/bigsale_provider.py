"""
ОПЦИОНАЛЬНЫЙ МОДУЛЬ: BigSaleApple userbot provider.

⚠️  ПРЕДУПРЕЖДЕНИЕ:
    Использование userbot-клиента (Telethon) нарушает Telegram ToS
    при использовании в автоматизированных целях без явного разрешения.
    Используйте только если:
    - Вы являетесь владельцем аккаунта
    - Понимаете риски бана аккаунта
    - Используете только в ознакомительных целях

Требует: telethon (pip install telethon)
Включить: PRICE_PROVIDER=userbot в .env

Как работает:
  1. Запускает userbot-сессию (Telethon)
  2. Отправляет команду /start или /catalog боту @BigSaleApple
  3. Ждёт ответа (парсит каталог с ценами)
  4. Возвращает список {sku, name, price, category}
"""
import logging
import re
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from telethon import TelegramClient
    from telethon.tl.types import Message as TgMessage
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logger.warning("Telethon not installed. Run: pip install telethon")

from bot.services.pricing import BasePriceProvider


class BigSaleAppleProvider(BasePriceProvider):
    """
    Provder that reads prices from @BigSaleApple via Telethon userbot.
    """

    def __init__(self, api_id: str, api_hash: str, session: str, bot_username: str):
        if not TELETHON_AVAILABLE:
            raise RuntimeError("Telethon not installed. Run: pip install telethon")
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.session = session
        self.bot_username = bot_username
        self._catalog: list[dict] = []

    async def _fetch_from_bot(self) -> list[dict]:
        """
        Connects to Telegram via userbot, sends message to BigSaleApple,
        parses response and extracts product catalog with prices.
        """
        results = []
        async with TelegramClient(self.session, self.api_id, self.api_hash) as client:
            # Send /start to get the catalog
            await client.send_message(self.bot_username, "/start")
            await asyncio.sleep(2)

            # Read last messages from bot
            messages = await client.get_messages(self.bot_username, limit=10)
            full_text = "\n".join(m.text or "" for m in messages if m.text)

            # Parse price patterns like: "iPhone 16 128GB — 89 990 ₽"
            # Adjust regex based on actual BigSaleApple bot format
            pattern = r"(.+?)\s*[—\-–]\s*([\d\s]+)\s*₽"
            for match in re.finditer(pattern, full_text):
                name = match.group(1).strip()
                price_str = match.group(2).replace(" ", "").replace("\u202f", "")
                try:
                    price = float(price_str)
                    results.append({
                        "sku": name.lower().replace(" ", "_")[:30],
                        "name": name,
                        "price": price,
                        "category": "Apple",
                    })
                except ValueError:
                    continue

        logger.info(f"BigSaleAppleProvider: fetched {len(results)} items")
        return results

    async def get_catalog(self) -> list[dict]:
        if not self._catalog:
            await self.refresh()
        return self._catalog

    async def refresh(self):
        try:
            self._catalog = await self._fetch_from_bot()
        except Exception as e:
            logger.error(f"BigSaleAppleProvider refresh error: {e}")
            self._catalog = []
