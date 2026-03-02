import math
from telegram import Update
from telegram.ext import (
    ContextTypes, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters,
)

from config import ADMIN_IDS, STATUSES, ITEMS_PER_PAGE, CURRENCY
from database.models import (
    get_stats, get_all_orders, get_order, get_order_items,
    update_order_status, get_categories, add_category, add_product,
    get_products, delete_product, get_all_users,
)
from keyboards.inline import admin_orders_kb, order_status_kb, delete_products_kb
from keyboards.reply import admin_menu_kb, main_menu_kb, cancel_kb

# Conversation states
(
    ADD_CAT_NAME, ADD_CAT_DESC, ADD_CAT_EMOJI,
    ADD_PROD_CAT, ADD_PROD_NAME, ADD_PROD_DESC,
    ADD_PROD_PRICE, ADD_PROD_PHOTO, ADD_PROD_STOCK,
    BROADCAST_TEXT,
) = range(30, 40)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id if update.effective_user else None
        if not uid or not is_admin(uid):
            if update.message:
                await update.message.reply_text("⛔ Доступ запрещён.")
            elif update.callback_query:
                await update.callback_query.answer("⛔ Доступ запрещён.", show_alert=True)
            return ConversationHandler.END
        return await func(update, context)
    return wrapper


# ─── Statistics ───────────────────────────────────────────────────────────────

@admin_only
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats()
    text = (
        "📊 <b>Статистика магазина</b>\n\n"
        f"👤 Пользователей: <b>{stats['users']}</b>\n"
        f"📦 Заказов: <b>{stats['orders']}</b>\n"
        f"🛍 Товаров: <b>{stats['products']}</b>\n"
        f"💰 Выручка: <b>{stats['revenue']:.2f}{CURRENCY}</b>"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=admin_menu_kb())


# ─── All orders ───────────────────────────────────────────────────────────────

@admin_only
async def show_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = get_all_orders()
    if not orders:
        await update.message.reply_text("📦 Заказов пока нет.", reply_markup=admin_menu_kb())
        return
    total_pages = math.ceil(len(orders) / ITEMS_PER_PAGE)
    page_orders = orders[:ITEMS_PER_PAGE]
    await update.message.reply_text(
        f"📦 <b>Все заказы</b> ({len(orders)} шт.):",
        parse_mode="HTML",
        reply_markup=admin_orders_kb(page_orders, 0, total_pages),
    )


async def admin_orders_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    page = int(query.data.split("_")[1])
    orders = get_all_orders()
    total_pages = math.ceil(len(orders) / ITEMS_PER_PAGE)
    page_orders = orders[page * ITEMS_PER_PAGE: (page + 1) * ITEMS_PER_PAGE]
    await query.edit_message_text(
        f"📦 <b>Все заказы</b> ({len(orders)} шт.):",
        parse_mode="HTML",
        reply_markup=admin_orders_kb(page_orders, page, total_pages),
    )


async def admin_order_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    order_id = int(query.data.split("_")[1])
    order = get_order(order_id)
    items = get_order_items(order_id)
    status = STATUSES.get(order["status"], order["status"])
    lines = [
        f"📦 <b>Заказ #{order_id}</b>",
        f"📅 {order['created_at'][:16]}",
        f"📊 Статус: {status}",
        f"📍 Адрес: {order.get('address') or '—'}",
        f"💬 Комментарий: {order.get('comment') or '—'}",
        "",
        "<b>Состав:</b>",
    ]
    for item in items:
        lines.append(f"• {item['product_name']} × {item['quantity']} = {item['price'] * item['quantity']:.2f}{CURRENCY}")
    lines.append(f"\n💰 <b>Итого: {order['total_price']:.2f}{CURRENCY}</b>")
    lines.append("\n<b>Изменить статус:</b>")
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=order_status_kb(order_id),
    )


async def set_order_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    _, order_id, status = query.data.split("_", 2)
    update_order_status(int(order_id), status)
    label = STATUSES.get(status, status)
    await query.edit_message_text(
        f"✅ Статус заказа #{order_id} изменён на: {label}"
    )
    order = get_order(int(order_id))
    if order:
        try:
            await context.bot.send_message(
                chat_id=order["user_id"],
                text=f"📦 Статус вашего заказа <b>#{order_id}</b> изменён на: {label}",
                parse_mode="HTML",
            )
        except Exception:
            pass


# ─── Add category conversation ────────────────────────────────────────────────

@admin_only
async def add_category_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📁 Введите название категории:", reply_markup=cancel_kb())
    return ADD_CAT_NAME


async def add_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cat_name"] = update.message.text.strip()
    await update.message.reply_text("📝 Введите описание (или «-» чтобы пропустить):")
    return ADD_CAT_DESC


async def add_category_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cat_desc"] = update.message.text.strip()
    await update.message.reply_text("😀 Введите эмодзи для категории (например 👗):")
    return ADD_CAT_EMOJI


async def add_category_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji = update.message.text.strip()
    name = context.user_data.get("cat_name", "")
    desc = context.user_data.get("cat_desc", "")
    if desc == "-":
        desc = ""
    add_category(name, desc, emoji)
    await update.message.reply_text(
        f"✅ Категория «{name}» добавлена!", reply_markup=admin_menu_kb()
    )
    context.user_data.clear()
    return ConversationHandler.END


# ─── Add product conversation ─────────────────────────────────────────────────

@admin_only
async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = get_categories()
    if not categories:
        await update.message.reply_text("❌ Сначала добавьте категорию!", reply_markup=admin_menu_kb())
        return ConversationHandler.END
    lines = ["📋 Выберите номер категории:\n"]
    for i, cat in enumerate(categories, 1):
        lines.append(f"{i}. {cat['emoji']} {cat['name']}")
    context.user_data["categories"] = categories
    await update.message.reply_text("\n".join(lines), reply_markup=cancel_kb())
    return ADD_PROD_CAT


async def add_product_cat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        idx = int(update.message.text.strip()) - 1
        categories = context.user_data.get("categories", [])
        context.user_data["prod_cat_id"] = categories[idx]["id"]
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Неверный номер. Попробуйте снова:")
        return ADD_PROD_CAT
    await update.message.reply_text("🏷 Введите название товара:")
    return ADD_PROD_NAME


async def add_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["prod_name"] = update.message.text.strip()
    await update.message.reply_text("📝 Введите описание товара (или «-»):")
    return ADD_PROD_DESC


async def add_product_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["prod_desc"] = update.message.text.strip()
    await update.message.reply_text("💰 Введите цену (например: 1500):")
    return ADD_PROD_PRICE


async def add_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text.strip().replace(",", "."))
        context.user_data["prod_price"] = price
    except ValueError:
        await update.message.reply_text("❌ Неверная цена. Введите число:")
        return ADD_PROD_PRICE
    await update.message.reply_text("📸 Отправьте фото товара (или «-» чтобы пропустить):")
    return ADD_PROD_PHOTO


async def add_product_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        context.user_data["prod_photo"] = update.message.photo[-1].file_id
    else:
        context.user_data["prod_photo"] = None
    await update.message.reply_text("📦 Введите количество на складе:")
    return ADD_PROD_STOCK


async def add_product_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        stock = int(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("❌ Введите целое число:")
        return ADD_PROD_STOCK
    d = context.user_data
    desc = d.get("prod_desc", "")
    if desc == "-":
        desc = ""
    add_product(
        category_id=d["prod_cat_id"],
        name=d["prod_name"],
        description=desc,
        price=d["prod_price"],
        photo_id=d.get("prod_photo"),
        stock=stock,
    )
    await update.message.reply_text(
        f"✅ Товар «{d['prod_name']}» добавлен!", reply_markup=admin_menu_kb()
    )
    context.user_data.clear()
    return ConversationHandler.END


# ─── Delete product ───────────────────────────────────────────────────────────

@admin_only
async def delete_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = get_products()
    if not products:
        await update.message.reply_text("😔 Товаров нет.", reply_markup=admin_menu_kb())
        return
    await update.message.reply_text(
        "🗑 Выберите товар для удаления:",
        reply_markup=delete_products_kb(products),
    )


async def delete_product_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        return
    product_id = int(query.data.split("_")[1])
    delete_product(product_id)
    await query.edit_message_text("✅ Товар удалён.")


# ─── Broadcast conversation ───────────────────────────────────────────────────

@admin_only
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📢 Введите текст рассылки (поддерживается HTML):",
        reply_markup=cancel_kb(),
    )
    return BROADCAST_TEXT


async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    users = get_all_users()
    sent = 0
    failed = 0
    for user in users:
        try:
            await context.bot.send_message(
                chat_id=user["telegram_id"],
                text=text,
                parse_mode="HTML",
            )
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(
        f"📢 Рассылка завершена!\n✅ Отправлено: {sent}\n❌ Ошибок: {failed}",
        reply_markup=admin_menu_kb(),
    )
    return ConversationHandler.END


async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Отменено.", reply_markup=admin_menu_kb())
    return ConversationHandler.END


def get_admin_handlers():
    add_cat_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Добавить категорию$"), add_category_start)],
        states={
            ADD_CAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_name)],
            ADD_CAT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_desc)],
            ADD_CAT_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_category_emoji)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ Отмена$"), admin_cancel)],
    )
    add_prod_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^➕ Добавить товар$"), add_product_start)],
        states={
            ADD_PROD_CAT:   [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_cat)],
            ADD_PROD_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_name)],
            ADD_PROD_DESC:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_desc)],
            ADD_PROD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_price)],
            ADD_PROD_PHOTO: [
                MessageHandler(filters.PHOTO, add_product_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_photo),
            ],
            ADD_PROD_STOCK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_product_stock)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ Отмена$"), admin_cancel)],
    )
    broadcast_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📢 Рассылка$"), broadcast_start)],
        states={
            BROADCAST_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_send)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌ Отмена$"), admin_cancel)],
    )
    return [
        MessageHandler(filters.Regex("^📊 Статистика$"), show_stats),
        MessageHandler(filters.Regex("^📦 Все заказы$"), show_all_orders),
        MessageHandler(filters.Regex("^🗑 Удалить товар$"), delete_product_start),
        CallbackQueryHandler(admin_orders_page_callback, pattern=r"^aordpage_\d+$"),
        CallbackQueryHandler(admin_order_detail_callback, pattern=r"^adminorder_\d+$"),
        CallbackQueryHandler(set_order_status_callback, pattern=r"^setstatus_\d+_.+$"),
        CallbackQueryHandler(delete_product_callback, pattern=r"^delprod_\d+$"),
        add_cat_conv,
        add_prod_conv,
        broadcast_conv,
    ]
