from telegram import Update
from telegram.ext import (
    ContextTypes, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters,
)

from database.models import search_products, get_product, add_to_cart, get_or_create_user
from keyboards.inline import product_detail_kb
from keyboards.reply import main_menu_kb, cancel_kb

WAITING_QUERY = 20


async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Введите название товара для поиска:",
        reply_markup=cancel_kb(),
    )
    return WAITING_QUERY


async def search_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if query == "❌ Отмена":
        await update.message.reply_text("❌ Поиск отменён.", reply_markup=main_menu_kb())
        return ConversationHandler.END
    results = search_products(query)
    if not results:
        await update.message.reply_text(
            f"😔 По запросу «{query}» ничего не найдено.\n\nПопробуйте другой запрос:",
            reply_markup=cancel_kb(),
        )
        return WAITING_QUERY
    await update.message.reply_text(
        f"🔍 Найдено товаров: <b>{len(results)}</b>",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
    for product in results[:10]:
        stock_text = f"✅ В наличии: {product['stock']} шт." if product["stock"] > 0 else "❌ Нет в наличии"
        text = (
            f"<b>{product['name']}</b>\n"
            f"{product.get('description') or ''}\n"
            f"💰 {product['price']:.2f}₽  {stock_text}"
        )
        kb = product_detail_kb(product["id"], product.get("category_id") or 0)
        if product.get("photo_id"):
            await update.message.reply_photo(
                photo=product["photo_id"],
                caption=text,
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)
    return ConversationHandler.END


async def search_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Поиск отменён.", reply_markup=main_menu_kb())
    return ConversationHandler.END


def get_search_handlers():
    search_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔍 Поиск$"), search_start)],
        states={
            WAITING_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_query)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ Отмена$"), search_cancel)],
    )
    return [search_conv]
