import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from bot.db.repository import (
    get_setting, set_setting,
    get_all_categories, get_all_products,
    set_category_visible, set_product_visible,
    get_recent_orders, get_order, update_order_status
)
from bot.keyboards import (
    kb_admin_main, kb_admin_markup, kb_admin_products,
    kb_admin_orders, kb_admin_order_detail
)

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


class AdminFSM(StatesGroup):
    waiting_markup_value = State()


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
        return
    await state.clear()
    await message.answer("👑 <b>Админ-панель</b>", reply_markup=kb_admin_main(), parse_mode="HTML")


@router.callback_query(F.data == "adm:back")
async def cb_adm_back(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id):
        await cb.answer("⛔", show_alert=True); return
    await state.clear()
    await cb.message.edit_text("👑 <b>Админ-панель</b>", reply_markup=kb_admin_main(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "adm:markup")
async def cb_adm_markup(cb: CallbackQuery):
    if not is_admin(cb.from_user.id):
        await cb.answer("⛔", show_alert=True); return
    mode = await get_setting("markup_mode") or "percent"
    value = await get_setting("markup_value") or "0"
    mode_str = "Процент (%)" if mode == "percent" else "Фиксированная (₽)"
    text = (
        f"💰 <b>Настройка наценки</b>\n\n"
        f"Режим: <b>{mode_str}</b>\n"
        f"Значение: <b>{value}{'%' if mode == 'percent' else ' ₽'}</b>\n\n"
        f"Выберите режим или измените значение:"
    )
    await cb.message.edit_text(text, reply_markup=kb_admin_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("adm:markup_mode:"))
async def cb_adm_markup_mode(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    mode = cb.data.split(":")[2]
    await set_setting("markup_mode", mode)
    value = await get_setting("markup_value") or "0"
    mode_str = "Процент (%)" if mode == "percent" else "Фиксированная (₽)"
    text = (
        f"💰 <b>Настройка наценки</b>\n\n"
        f"Режим изменён: <b>{mode_str}</b>\n"
        f"Значение: <b>{value}{'%' if mode == 'percent' else ' ₽'}</b>"
    )
    await cb.message.edit_text(text, reply_markup=kb_admin_markup(), parse_mode="HTML")
    await cb.answer("Режим изменён ✅")


@router.callback_query(F.data == "adm:markup_edit")
async def cb_adm_markup_edit(cb: CallbackQuery, state: FSMContext):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    mode = await get_setting("markup_mode") or "percent"
    unit = "%" if mode == "percent" else "₽"
    await cb.message.edit_text(
        f"✏️ Введите новое значение наценки ({unit})\n(только число, например: 15):",
        parse_mode="HTML"
    )
    await state.set_state(AdminFSM.waiting_markup_value)
    await cb.answer()


@router.message(AdminFSM.waiting_markup_value)
async def fsm_markup_value(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    text = message.text.strip().replace(",", ".")
    try:
        value = float(text)
        if value < 0 or value > 10000:
            raise ValueError
    except ValueError:
        await message.answer("❌ Некорректное значение. Введите число от 0 до 10000:")
        return
    await set_setting("markup_value", str(value))
    await state.clear()
    mode = await get_setting("markup_mode") or "percent"
    unit = "%" if mode == "percent" else "₽"
    await message.answer(
        f"✅ Наценка установлена: <b>{value}{unit}</b>",
        reply_markup=kb_admin_main(), parse_mode="HTML"
    )


@router.callback_query(F.data == "adm:refresh")
async def cb_adm_refresh(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    await cb.message.edit_text("🔄 Обновление каталога...", parse_mode="HTML")
    try:
        # Access price_calc via dispatcher
        from bot.services.pricing import MockProvider, PriceCalculator
        calc = PriceCalculator(MockProvider())
        await calc.refresh_catalog()
        await cb.message.edit_text(
            "✅ <b>Каталог обновлён</b>", reply_markup=kb_admin_main(), parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Refresh error: {e}")
        await cb.message.edit_text(
            f"❌ Ошибка обновления:\n<code>{e}</code>",
            reply_markup=kb_admin_main(), parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data == "adm:products")
async def cb_adm_products(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    cats = await get_all_categories()
    prods = await get_all_products()
    text = "📦 <b>Управление товарами</b>\n\n✅ — видимый | ❌ — скрытый\nНажмите для переключения:"
    await cb.message.edit_text(text, reply_markup=kb_admin_products(cats, prods), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("adm:toggle_cat:"))
async def cb_adm_toggle_cat(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    cat_id = int(cb.data.split(":")[2])
    cats = await get_all_categories()
    cat = next((c for c in cats if c["id"] == cat_id), None)
    if cat:
        await set_category_visible(cat_id, not bool(cat["visible"]))
    cats = await get_all_categories()
    prods = await get_all_products()
    await cb.message.edit_reply_markup(reply_markup=kb_admin_products(cats, prods))
    await cb.answer("Обновлено ✅")


@router.callback_query(F.data.startswith("adm:toggle_prod:"))
async def cb_adm_toggle_prod(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    prod_id = int(cb.data.split(":")[2])
    prods = await get_all_products()
    prod = next((p for p in prods if p["id"] == prod_id), None)
    if prod:
        await set_product_visible(prod_id, not bool(prod["visible"]))
    cats = await get_all_categories()
    prods = await get_all_products()
    await cb.message.edit_reply_markup(reply_markup=kb_admin_products(cats, prods))
    await cb.answer("Обновлено ✅")


@router.callback_query(F.data == "adm:orders")
async def cb_adm_orders(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    orders = await get_recent_orders(20)
    if not orders:
        await cb.message.edit_text("📋 Заказов пока нет", reply_markup=kb_admin_main(), parse_mode="HTML")
    else:
        await cb.message.edit_text(
            "📋 <b>Последние заказы</b>:",
            reply_markup=kb_admin_orders(orders), parse_mode="HTML"
        )
    await cb.answer()


@router.callback_query(F.data.startswith("adm:order:"))
async def cb_adm_order_detail(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    order_id = int(cb.data.split(":")[2])
    order = await get_order(order_id)
    if not order:
        await cb.answer("Заказ не найден", show_alert=True); return
    from bot.services.pricing import format_price
    status_map = {"new": "🆕 Новый", "done": "✅ Выполнен", "cancelled": "❌ Отменён"}
    text = (
        f"📋 <b>Заказ #{order['id']}</b>\n\n"
        f"Товар: {order['product_name']}\n"
        f"Сумма: {format_price(order['price'])}\n"
        f"Контакт: {order['contact']}\n"
        f"Комментарий: {order['comment']}\n"
        f"Статус: {status_map.get(order['status'], order['status'])}\n"
        f"Дата: {order['created_at']}"
    )
    await cb.message.edit_text(text, reply_markup=kb_admin_order_detail(order_id), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("adm:order_status:"))
async def cb_adm_order_status(cb: CallbackQuery):
    if not is_admin(cb.from_user.id): await cb.answer("⛔", show_alert=True); return
    parts = cb.data.split(":")
    order_id, status = int(parts[2]), parts[3]
    await update_order_status(order_id, status)
    await cb_adm_orders(cb)
