import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.db.repository import get_product, create_order, upsert_user
from bot.keyboards import kb_cancel_order, kb_confirm_order, kb_back_main
from bot.services.pricing import format_price
import aiosqlite
from config import DB_PATH, ADMIN_IDS

router = Router()
logger = logging.getLogger(__name__)


class OrderFSM(StatesGroup):
    waiting_contact = State()
    waiting_comment = State()
    confirming = State()


@router.callback_query(F.data.startswith("buy:"))
async def cb_buy(cb: CallbackQuery, state: FSMContext):
    prod_id = int(cb.data.split(":")[1])
    product = await get_product(prod_id)
    if not product:
        await cb.answer("Товар недоступен", show_alert=True)
        return

    await state.update_data(product_id=prod_id, product_name=product["name"], base_price=product["base_price"])
    text = (
        f"🛒 <b>Оформление заказа</b>\n\n"
        f"Товар: <b>{product['name']}</b>\n\n"
        f"Пожалуйста, введите ваш <b>контакт</b> для связи\n"
        f"(номер телефона, @username или email):"
    )
    await cb.message.edit_text(text, reply_markup=kb_cancel_order(), parse_mode="HTML")
    await state.set_state(OrderFSM.waiting_contact)
    await cb.answer()


@router.message(OrderFSM.waiting_contact)
async def fsm_contact(message: Message, state: FSMContext):
    contact = message.text.strip()
    if len(contact) < 3:
        await message.answer("Введите корректный контакт:", reply_markup=kb_cancel_order())
        return
    await state.update_data(contact=contact)
    await message.answer(
        "💬 Добавьте комментарий к заказу\n(например: цвет, объём памяти) или напишите <b>—</b> если нет:",
        reply_markup=kb_cancel_order(), parse_mode="HTML"
    )
    await state.set_state(OrderFSM.waiting_comment)


@router.message(OrderFSM.waiting_comment)
async def fsm_comment(message: Message, state: FSMContext):
    comment = message.text.strip()
    data = await state.get_data()

    # Calculate price with markup
    base_price = data["base_price"]
    from bot.db.repository import get_setting
    mode = await get_setting("markup_mode") or "percent"
    value = float(await get_setting("markup_value") or "0")
    if mode == "percent":
        final_price = round(base_price * (1 + value / 100))
    else:
        final_price = round(base_price + value)

    await state.update_data(comment=comment, final_price=final_price)

    text = (
        f"📋 <b>Подтвердите заказ</b>\n\n"
        f"Товар: <b>{data['product_name']}</b>\n"
        f"Цена: <b>{format_price(final_price)}</b>\n"
        f"Контакт: {data['contact']}\n"
        f"Комментарий: {comment}\n\n"
        f"Всё верно?"
    )
    await message.answer(text, reply_markup=kb_confirm_order(), parse_mode="HTML")
    await state.set_state(OrderFSM.confirming)


@router.callback_query(OrderFSM.confirming, F.data == "confirm_order")
async def fsm_confirm(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = await create_order(
        user_id=cb.from_user.id,
        product_id=data["product_id"],
        product_name=data["product_name"],
        price=data["final_price"],
        contact=data["contact"],
        comment=data["comment"],
    )
    await state.clear()

    text = (
        f"✅ <b>Заказ #{order_id} оформлен!</b>\n\n"
        f"Товар: {data['product_name']}\n"
        f"Сумма: {format_price(data['final_price'])}\n\n"
        f"Наш менеджер свяжется с вами по контакту:\n{data['contact']}\n\n"
        f"Спасибо за покупку! 🍎"
    )
    await cb.message.edit_text(text, reply_markup=kb_back_main(), parse_mode="HTML")
    await cb.answer("Заказ оформлен!")

    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await cb.bot.send_message(
                admin_id,
                f"🆕 <b>Новый заказ #{order_id}</b>\n"
                f"Товар: {data['product_name']}\n"
                f"Сумма: {format_price(data['final_price'])}\n"
                f"Контакт: {data['contact']}\n"
                f"Комментарий: {data['comment']}\n"
                f"Пользователь: @{cb.from_user.username or cb.from_user.full_name}",
                parse_mode="HTML"
            )
        except Exception as e:
            logger.warning(f"Failed to notify admin {admin_id}: {e}")


@router.callback_query(F.data == "cancel_order")
async def cb_cancel_order(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    from bot.handlers.user.menu import MAIN_TEXT
    from bot.keyboards import kb_main_menu
    await cb.message.edit_text(MAIN_TEXT, reply_markup=kb_main_menu(), parse_mode="HTML")
    await cb.answer("Заказ отменён")
