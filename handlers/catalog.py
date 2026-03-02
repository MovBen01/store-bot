import math
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

from config import PRODUCTS_PER_PAGE
from database.models import get_categories, get_products, get_product, get_category, add_to_cart, get_or_create_user
from keyboards.inline import categories_kb, products_kb, product_detail_kb
from keyboards.reply import main_menu_kb


async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = get_categories()
    if not categories:
        await update.message.reply_text(
            "😔 Категории пока не добавлены.", reply_markup=main_menu_kb()
        )
        return
    await update.message.reply_text(
        "🛍 <b>Каталог товаров</b>\n\nВыберите категорию:",
        parse_mode="HTML",
        reply_markup=categories_kb(categories),
    )


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = int(query.data.split("_")[1])
    await _show_products_page(query, cat_id, 0)


async def products_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    _, cat_id, page = query.data.split("_")
    await _show_products_page(query, int(cat_id), int(page))


async def _show_products_page(query, cat_id: int, page: int):
    products = get_products(category_id=cat_id)
    category = get_category(cat_id)
    if not products:
        await query.edit_message_text(
            f"😔 В категории <b>{category['name']}</b> пока нет товаров.",
            parse_mode="HTML",
            reply_markup=categories_kb(get_categories()),
        )
        return
    total_pages = math.ceil(len(products) / PRODUCTS_PER_PAGE)
    page_products = products[page * PRODUCTS_PER_PAGE: (page + 1) * PRODUCTS_PER_PAGE]
    text = f"{category['emoji']} <b>{category['name']}</b>\n\nВыберите товар:"
    await query.edit_message_text(
        text,
        parse_mode="HTML",
        reply_markup=products_kb(page_products, page, total_pages, cat_id),
    )


async def back_to_cats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    categories = get_categories()
    await query.edit_message_text(
        "🛍 <b>Каталог товаров</b>\n\nВыберите категорию:",
        parse_mode="HTML",
        reply_markup=categories_kb(categories),
    )


async def product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split("_")[1])
    product = get_product(product_id)
    if not product:
        await query.answer("Товар не найден", show_alert=True)
        return
    stock_text = f"✅ В наличии: {product['stock']} шт." if product["stock"] > 0 else "❌ Нет в наличии"
    text = (
        f"<b>{product['name']}</b>\n\n"
        f"{product.get('description') or ''}\n\n"
        f"💰 Цена: <b>{product['price']:.2f}₽</b>\n"
        f"{stock_text}"
    )
    cat_id = product.get("category_id") or 0
    kb = product_detail_kb(product_id, cat_id)
    if product.get("photo_id"):
        try:
            await query.message.delete()
            await query.message.chat.send_photo(
                photo=product["photo_id"],
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        except Exception:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    else:
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=kb)


async def add_to_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split("_")[1])
    product = get_product(product_id)
    if not product or product["stock"] <= 0:
        await query.answer("❌ Товар недоступен", show_alert=True)
        return
    user = get_or_create_user(query.from_user.id, query.from_user.username, query.from_user.full_name)
    add_to_cart(user["id"], product_id)
    await query.answer(f"✅ {product['name']} добавлен в корзину!", show_alert=True)


async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()


def get_catalog_handlers():
    return [
        MessageHandler(filters.Regex("^🛍 Каталог$"), show_catalog),
        CallbackQueryHandler(category_callback, pattern=r"^cat_\d+$"),
        CallbackQueryHandler(products_page_callback, pattern=r"^ppage_\d+_\d+$"),
        CallbackQueryHandler(back_to_cats_callback, pattern=r"^back_cats$"),
        CallbackQueryHandler(product_callback, pattern=r"^prod_\d+$"),
        CallbackQueryHandler(add_to_cart_callback, pattern=r"^addcart_\d+$"),
        CallbackQueryHandler(noop_callback, pattern=r"^noop$"),
    ]
