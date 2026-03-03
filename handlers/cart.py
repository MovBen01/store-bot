from telegram import Update
from telegram.ext import (
    ContextTypes, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters,
)

from config import CURRENCY
from database.models import (
    get_cart, get_cart_total, clear_cart, update_cart_quantity,
    get_or_create_user, create_order, get_user,
)
from keyboards.inline import cart_kb
from keyboards.reply import main_menu_kb, cancel_kb

WAITING_ADDRESS = 10
WAITING_COMMENT = 11


def _cart_text(items: list, total: float) -> str:
    if not items:
        return "🛒 Ваша корзина пуста."
    lines = ["🛒 <b>Ваша корзина:</b>\n"]
    for item in items:
        lines.append(
            f"• {item['name']} × {item['quantity']} = {item['price'] * item['quantity']:.2f}{CURRENCY}"
        )
    lines.append(f"\n💰 <b>Итого: {total:.2f}{CURRENCY}</b>")
    return "\n".join(lines)


async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_or_create_user(
        update.effective_user.id,
        update.effective_user.username,
        update.effective_user.full_name,
    )
    items = get_cart(user["id"])
    total = get_cart_total(user["id"])
    text = _cart_text(items, total)
    if items:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=cart_kb(items))
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_kb())


async def cart_inc_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split("_")[1])
    user = get_or_create_user(query.from_user.id)
    items = get_cart(user["id"])
    item = next((i for i in items if i["product_id"] == product_id), None)
    if item:
        new_qty = item["quantity"] + 1
        if new_qty > item["stock"]:
            await query.answer("❌ Больше нет в наличии", show_alert=True)
            return
        update_cart_quantity(user["id"], product_id, new_qty)
    await _refresh_cart(query, user["id"])


async def cart_dec_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split("_")[1])
    user = get_or_create_user(query.from_user.id)
    items = get_cart(user["id"])
    item = next((i for i in items if i["product_id"] == product_id), None)
    if item:
        update_cart_quantity(user["id"], product_id, item["quantity"] - 1)
    await _refresh_cart(query, user["id"])


async def cart_del_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split("_")[1])
    user = get_or_create_user(query.from_user.id)
    update_cart_quantity(user["id"], product_id, 0)
    await _refresh_cart(query, user["id"])


async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_or_create_user(query.from_user.id)
    clear_cart(user["id"])
    await query.edit_message_text("🗑 Корзина очищена.")


async def _refresh_cart(query, user_id: int):
    items = get_cart(user_id)
    total = get_cart_total(user_id)
    text = _cart_text(items, total)
    if items:
        try:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=cart_kb(items))
        except Exception:
            pass
    else:
        await query.edit_message_text("🛒 Корзина пуста.", parse_mode="HTML")


# ─── Checkout conversation ─────────────────────────────────────────────────────

async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_or_create_user(query.from_user.id)
    items = get_cart(user["id"])
    if not items:
        await query.answer("Корзина пуста!", show_alert=True)
        return
    saved_address = get_user(query.from_user.id).get("address")
    context.user_data["checkout_user_id"] = user["id"]
    if saved_address:
        context.user_data["checkout_address"] = saved_address
        await query.message.reply_text(
            f"📍 Использовать сохранённый адрес?\n<b>{saved_address}</b>\n\n"
            "Или введите новый адрес:",
            parse_mode="HTML",
            reply_markup=cancel_kb(),
        )
    else:
        await query.message.reply_text(
            "📍 Введите адрес доставки:",
            reply_markup=cancel_kb(),
        )
    return WAITING_ADDRESS


async def checkout_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    context.user_data["checkout_address"] = address
    await update.message.reply_text(
        "💬 Добавить комментарий к заказу? (или отправьте «-» чтобы пропустить):",
        reply_markup=cancel_kb(),
    )
    return WAITING_COMMENT


async def checkout_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment = update.message.text.strip()
    if comment == "-":
        comment = ""
    user_id = context.user_data.get("checkout_user_id")
    address = context.user_data.get("checkout_address", "")
    order_id = create_order(user_id, address, comment)
    if not order_id:
        await update.message.reply_text("❌ Ошибка при создании заказа.", reply_markup=main_menu_kb())
        return ConversationHandler.END
    await update.message.reply_text(
        f"✅ <b>Заказ #{order_id} оформлен!</b>\n\n"
        f"📍 Адрес: {address}\n"
        f"💬 Комментарий: {comment or '—'}\n\n"
        "Мы свяжемся с вами для подтверждения. Спасибо! 🙏",
        parse_mode="HTML",
        reply_markup=main_menu_kb(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def checkout_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Оформление отменено.", reply_markup=main_menu_kb())
    return ConversationHandler.END


def get_cart_handlers():
    checkout_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(checkout_callback, pattern=r"^checkout$")],
        states={
            WAITING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_address)],
            WAITING_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_comment)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ Отмена$"), checkout_cancel)],
    )
    return [
        MessageHandler(filters.Regex("^🛒 Корзина$"), show_cart),
        CallbackQueryHandler(cart_inc_callback, pattern=r"^cartinc_\d+$"),
        CallbackQueryHandler(cart_dec_callback, pattern=r"^cartdec_\d+$"),
        CallbackQueryHandler(cart_del_callback, pattern=r"^cartdel_\d+$"),
        CallbackQueryHandler(clear_cart_callback, pattern=r"^clearcart$"),
        checkout_conv,
    ]
