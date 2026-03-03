from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

from config import ADMIN_IDS
from database.models import get_or_create_user, update_user_phone, update_user_address, get_user
from keyboards.reply import main_menu_kb, admin_menu_kb, contact_kb, cancel_kb

WAITING_PHONE = 1
WAITING_ADDRESS = 2


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username, user.full_name)
    text = (
        f"👋 Привет, <b>{user.first_name}</b>!\n\n"
        "Добро пожаловать в наш магазин! 🛍\n\n"
        "Используй меню ниже для навигации:"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_kb())


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "ℹ️ <b>Помощь</b>\n\n"
        "🛍 <b>Каталог</b> — просмотр товаров по категориям\n"
        "🔍 <b>Поиск</b> — найти товар по названию\n"
        "🛒 <b>Корзина</b> — управление корзиной\n"
        "📦 <b>Мои заказы</b> — история заказов\n"
        "👤 <b>Профиль</b> — ваши данные\n\n"
        "По вопросам пишите: @support"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_kb())


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = get_user(update.effective_user.id)
    if not user_data:
        await update.message.reply_text("Профиль не найден. Нажмите /start")
        return
    text = (
        "👤 <b>Ваш профиль</b>\n\n"
        f"👤 Имя: {user_data.get('full_name') or '—'}\n"
        f"📱 Телефон: {user_data.get('phone') or '—'}\n"
        f"📍 Адрес: {user_data.get('address') or '—'}\n\n"
        "Для изменения данных используйте команды:\n"
        "/setphone — изменить телефон\n"
        "/setaddress — изменить адрес"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_menu_kb())


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Доступ запрещён.")
        return
    await update.message.reply_text(
        "🔧 <b>Панель администратора</b>",
        parse_mode="HTML",
        reply_markup=admin_menu_kb(),
    )


# ─── Set phone conversation ────────────────────────────────────────────────────

async def setphone_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📱 Отправьте ваш номер телефона:",
        reply_markup=contact_kb(),
    )
    return WAITING_PHONE


async def setphone_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.strip()
    update_user_phone(update.effective_user.id, phone)
    await update.message.reply_text(
        f"✅ Телефон сохранён: {phone}", reply_markup=main_menu_kb()
    )
    return ConversationHandler.END


# ─── Set address conversation ──────────────────────────────────────────────────

async def setaddress_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📍 Введите ваш адрес доставки:",
        reply_markup=cancel_kb(),
    )
    return WAITING_ADDRESS


async def setaddress_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    address = update.message.text.strip()
    update_user_address(update.effective_user.id, address)
    await update.message.reply_text(
        f"✅ Адрес сохранён: {address}", reply_markup=main_menu_kb()
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Отменено.", reply_markup=main_menu_kb())
    return ConversationHandler.END


def get_start_handlers():
    phone_conv = ConversationHandler(
        entry_points=[CommandHandler("setphone", setphone_start)],
        states={WAITING_PHONE: [MessageHandler(filters.CONTACT | filters.TEXT & ~filters.COMMAND, setphone_receive)]},
        fallbacks=[MessageHandler(filters.Regex("^❌ Отмена$"), cancel)],
    )
    address_conv = ConversationHandler(
        entry_points=[CommandHandler("setaddress", setaddress_start)],
        states={WAITING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, setaddress_receive)]},
        fallbacks=[MessageHandler(filters.Regex("^❌ Отмена$"), cancel)],
    )
    return [
        CommandHandler("start", start),
        CommandHandler("admin", admin_panel),
        MessageHandler(filters.Regex("^ℹ️ Помощь$"), help_handler),
        MessageHandler(filters.Regex("^👤 Профиль$"), profile),
        MessageHandler(filters.Regex("^🏠 Главное меню$"), start),
        phone_conv,
        address_conv,
    ]
