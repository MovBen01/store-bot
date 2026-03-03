import logging
from abc import ABC, abstractmethod
from bot.db.repository import get_setting, set_setting, update_product_price, get_all_products

logger = logging.getLogger(__name__)


class BasePriceProvider(ABC):
    @abstractmethod
    async def get_catalog(self) -> list:
        pass

    @abstractmethod
    async def refresh(self):
        pass


class MockProvider(BasePriceProvider):
    async def get_catalog(self) -> list:
        products = await get_all_products()
        return [{"sku": str(p["id"]), "name": p["name"], "price": p["base_price"]} for p in products]

    async def refresh(self):
        logger.info("MockProvider: nothing to refresh")


class PriceCalculator:
    def __init__(self, provider: BasePriceProvider):
        self.provider = provider

    async def apply_markup(self, base_price: float) -> float:
        mode = await get_setting("markup_mode") or "percent"
        value = float(await get_setting("markup_value") or "0")
        if mode == "percent":
            return round(base_price * (1 + value / 100))
        return round(base_price + value)

    async def refresh_catalog(self):
        catalog = await self.provider.get_catalog()
        for item in catalog:
            if "sku" in item and "price" in item:
                try:
                    await update_product_price(str(item["sku"]), float(item["price"]))
                except Exception as e:
                    logger.warning(f"Failed to update {item['sku']}: {e}")
        logger.info(f"Catalog refreshed: {len(catalog)} items")


def format_price(price: float) -> str:
    return f"{int(price):,} ₽".replace(",", " ")
