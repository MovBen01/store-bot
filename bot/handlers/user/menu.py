import logging
import aiosqlite
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart

from bot.db.repository import upsert_user, get_categories, get_products, get_product
from bot.keyboards import (
    kb_main_menu, kb_categories, kb_products, kb_product_card, kb_back_main
)
from bot.services.pricing import format_price
from bot.db.repository import get_setting
from config import DB_PATH, WEBAPP_URL

router = Router()
logger = logging.getLogger(__name__)

SUPPORT_TEXT = (
    "💬 <b>Поддержка</b>\n\n"
    "По всем вопросам пишите: @support_username\n"
    "Время работы: 9:00 – 21:00 (МСК)"
)

FAQ_TEXT = (
    "❓ <b>FAQ</b>\n\n"
    "<b>Как сделать заказ?</b>\n"
    "Выберите товар в каталоге и нажмите «Купить».\n\n"
    "<b>Как оплатить?</b>\n"
    "Менеджер свяжется с вами после оформления заказа.\n\n"
    "<b>Доставка?</b>\n"
    "Курьером по городу или СДЭК по России.\n\n"
    "<b>Гарантия?</b>\n"
    "1 год официальной гарантии Apple."
)


def kb_start(webapp_url: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if webapp_url:
        b.row(InlineKeyboardButton(
            text="🛍 Открыть магазин",
            web_app=WebAppInfo(url=webapp_url)
        ))
    b.row(InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders"))
    b.row(
        InlineKeyboardButton(text="💬 Поддержка", callback_data="support"),
        InlineKeyboardButton(text="❓ FAQ", callback_data="faq")
    )
    if not webapp_url:
        b.row(InlineKeyboardButton(text="🛍 Каталог (текст)", callback_data="catalog"))
    return b.as_markup()


async def calc_price(base_price: float) -> float:
    mode = await get_setting("markup_mode") or "percent"
    value = float(await get_setting("markup_value") or "0")
    if mode == "percent":
        return round(base_price * (1 + value / 100))
    return round(base_price + value)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await upsert_user(message.from_user.id, message.from_user.username or "", message.from_user.full_name)
    text = (
        f"🍎 <b>Apple Store</b>\n\n"
        f"Привет, {message.from_user.first_name}!\n"
        f"Добро пожаловать в магазин Apple-техники.\n\n"
        f"Нажмите кнопку ниже, чтобы открыть магазин 👇"
    )
    await message.answer(text, reply_markup=kb_start(WEBAPP_URL), parse_mode="HTML")


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(cb: CallbackQuery):
    text = "🍎 <b>Apple Store</b>\n\nВыберите раздел:"
    await cb.message.edit_text(text, reply_markup=kb_start(WEBAPP_URL), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "catalog")
async def cb_catalog(cb: CallbackQuery):
    cats = await get_categories()
    text = "🛍 <b>Каталог</b>\n\nВыберите категорию:"
    await cb.message.edit_text(text, reply_markup=kb_categories(cats), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("cat:"))
async def cb_category(cb: CallbackQuery):
    cat_id = int(cb.data.split(":")[1])
    products = await get_products(cat_id)
    if not products:
        await cb.answer("В этой категории пока нет товаров", show_alert=True)
        return
    cats = await get_categories()
    cat = next((c for c in cats if c["id"] == cat_id), None)
    cat_name = f"{cat['emoji']} {cat['name']}" if cat else "Категория"
    text = f"<b>{cat_name}</b>\n\nВыберите товар:"
    await cb.message.edit_text(text, reply_markup=kb_products(products), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("prod:"))
async def cb_product(cb: CallbackQuery):
    prod_id = int(cb.data.split(":")[1])
    product = await get_product(prod_id)
    if not product:
        await cb.answer("Товар не найден", show_alert=True)
        return

    display_price = await calc_price(product["base_price"])

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT category_id FROM products WHERE id=?", (prod_id,)) as cur:
            row = await cur.fetchone()
            cat_id = row[0] if row else 0

    text = (
        f"<b>{product['name']}</b>\n\n"
        f"📝 {product['description']}\n\n"
        f"💰 Цена: <b>{format_price(display_price)}</b>\n\n"
        f"Нажмите «Купить», чтобы оформить заказ."
    )
    await cb.message.edit_text(text, reply_markup=kb_product_card(prod_id, cat_id), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "support")
async def cb_support(cb: CallbackQuery):
    await cb.message.edit_text(SUPPORT_TEXT, reply_markup=kb_back_main(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "faq")
async def cb_faq(cb: CallbackQuery):
    await cb.message.edit_text(FAQ_TEXT, reply_markup=kb_back_main(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "my_orders")
async def cb_my_orders(cb: CallbackQuery):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, product_name, price, status, created_at FROM orders WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
            (cb.from_user.id,)
        ) as cur:
            orders = await cur.fetchall()

    if not orders:
        text = "📦 <b>Мои заказы</b>\n\nУ вас пока нет заказов."
    else:
        lines = ["📦 <b>Мои заказы</b>\n"]
        for o in orders:
            status_map = {"new": "🆕 Новый", "done": "✅ Выполнен", "cancelled": "❌ Отменён"}
            s = status_map.get(o["status"], o["status"])
            lines.append(f"#{o['id']} — {o['product_name']}\n{format_price(o['price'])} | {s}\n{o['created_at'][:10]}\n")
        text = "\n".join(lines)

    await cb.message.edit_text(text, reply_markup=kb_back_main(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "noop")
async def cb_noop(cb: CallbackQuery):
    await cb.answer()
