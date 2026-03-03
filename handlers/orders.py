import math
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

from config import STATUSES, ITEMS_PER_PAGE, CURRENCY
from database.models import get_orders, get_order, get_order_items, get_or_create_user
from keyboards.inline import orders_list_kb


def _order_text(order: dict, items: list) -> str:
    status = STATUSES.get(order["status"], order["status"])
    lines = [
        f"📦 <b>Заказ #{order['id']}</b>",
        f"📅 Дата: {order['created_at'][:16]}",
        f"📊 Статус: {status}",
        f"📍 Адрес: {order.get('address') or '—'}",
        "",
        "<b>Состав заказа:</b>",
    ]
    for item in items:
        lines.append(
            f"• {item['product_name']} × {item['quantity']} = {item['price'] * item['quantity']:.2f}{CURRENCY}"
        )
    lines.append(f"\n💰 <b>Итого: {order['total_price']:.2f}{CURRENCY}</b>")
    if order.get("comment"):
        lines.append(f"💬 Комментарий: {order['comment']}")
    return "\n".join(lines)


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(
        update.effective_user.id,
        update.effective_user.username,
        update.effective_user.full_name,
    )
    orders = get_orders(user["id"])
    if not orders:
        await update.message.reply_text("📦 У вас ещё нет заказов.")
        return
    total_pages = math.ceil(len(orders) / ITEMS_PER_PAGE)
    page_orders = orders[:ITEMS_PER_PAGE]
    await update.message.reply_text(
        f"📦 <b>Ваши заказы</b> ({len(orders)} шт.):",
        parse_mode="HTML",
        reply_markup=orders_list_kb(page_orders, 0, total_pages),
    )


async def orders_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[1])
    user = get_or_create_user(query.from_user.id)
    orders = get_orders(user["id"])
    total_pages = math.ceil(len(orders) / ITEMS_PER_PAGE)
    page_orders = orders[page * ITEMS_PER_PAGE: (page + 1) * ITEMS_PER_PAGE]
    await query.edit_message_text(
        f"📦 <b>Ваши заказы</b> ({len(orders)} шт.):",
        parse_mode="HTML",
        reply_markup=orders_list_kb(page_orders, page, total_pages),
    )


async def order_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    order_id = int(query.data.split("_")[1])
    order = get_order(order_id)
    if not order:
        await query.answer("Заказ не найден", show_alert=True)
        return
    items = get_order_items(order_id)
    text = _order_text(order, items)
    await query.edit_message_text(text, parse_mode="HTML")


def get_orders_handlers():
    return [
        MessageHandler(filters.Regex("^📦 Мои заказы$"), show_orders),
        CallbackQueryHandler(orders_page_callback, pattern=r"^ordpage_\d+$"),
        CallbackQueryHandler(order_detail_callback, pattern=r"^order_\d+$"),
    ]
