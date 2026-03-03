"""
Search handler.
Flow:
  /search button → edit message to "enter query" prompt
  User types query → bot edits same message with results (FSM: SearchFSM.waiting_query)
  Pagination → search_page callback (query encoded in callback_data, max 20 chars)
  Product card → search_prod callback → edit to product card with "back to results"
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.db.repository import search_products, count_search_results, get_product
from bot.db.repository import get_setting
from bot.keyboards import (
    kb_search_results, kb_search_product_card, kb_search_empty, kb_cancel_order,
    SEARCH_PAGE_SIZE
)
from bot.services.pricing import format_price

router = Router()
logger = logging.getLogger(__name__)

SEARCH_PROMPT = (
    "🔍 <b>Поиск по каталогу</b>\n\n"
    "Введите название товара, категорию или ключевое слово\n"
    "(например: <i>iPhone 16</i>, <i>MacBook</i>, <i>AirPods</i>):"
)


class SearchFSM(StatesGroup):
    waiting_query = State()


# ---------- Trigger search ----------
@router.callback_query(F.data == "search")
async def cb_search(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SearchFSM.waiting_query)
    await state.update_data(search_msg_id=cb.message.message_id)
    await cb.message.edit_text(SEARCH_PROMPT, reply_markup=kb_cancel_order(), parse_mode="HTML")
    await cb.answer()


# ---------- Receive query text ----------
@router.message(SearchFSM.waiting_query)
async def fsm_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("Введите минимум 2 символа:", reply_markup=kb_cancel_order())
        return

    data = await state.get_data()
    msg_id = data.get("search_msg_id")
    await state.clear()

    # Delete user's text message to keep chat clean
    try:
        await message.delete()
    except Exception:
        pass

    total = await count_search_results(query)
    products = await search_products(query, limit=SEARCH_PAGE_SIZE, offset=0)

    if not products or total == 0:
        text = (
            f"🔍 По запросу «<b>{query}</b>» ничего не найдено.\n\n"
            f"Попробуйте другое название или выберите из каталога."
        )
        kb = kb_search_empty()
    else:
        text = _build_results_text(query, products, page=0, total=total)
        kb = kb_search_results(products, query, page=0, total=total)

    # Edit the original "enter query" message
    if msg_id:
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=msg_id,
                text=text,
                reply_markup=kb,
                parse_mode="HTML"
            )
            return
        except Exception:
            pass

    # Fallback: send new message
    await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ---------- Pagination ----------
@router.callback_query(F.data.startswith("search_page:"))
async def cb_search_page(cb: CallbackQuery):
    parts = cb.data.split(":", 2)
    page = int(parts[1])
    query = parts[2] if len(parts) > 2 else ""

    total = await count_search_results(query)
    products = await search_products(query, limit=SEARCH_PAGE_SIZE, offset=page * SEARCH_PAGE_SIZE)

    if not products:
        await cb.answer("Нет результатов", show_alert=True)
        return

    text = _build_results_text(query, products, page=page, total=total)
    kb = kb_search_results(products, query, page=page, total=total)

    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await cb.answer()


# ---------- Product card from search ----------
@router.callback_query(F.data.startswith("search_prod:"))
async def cb_search_product(cb: CallbackQuery):
    # format: search_prod:{prod_id}:{page}:{query}
    parts = cb.data.split(":", 3)
    prod_id = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 else 0
    query = parts[3] if len(parts) > 3 else ""

    product = await get_product(prod_id)
    if not product:
        await cb.answer("Товар не найден", show_alert=True)
        return

    # Apply markup
    mode = await get_setting("markup_mode") or "percent"
    value = float(await get_setting("markup_value") or "0")
    base = product["base_price"]
    price = round(base * (1 + value / 100)) if mode == "percent" else round(base + value)

    text = (
        f"<b>{product['name']}</b>\n\n"
        f"📝 {product['description']}\n\n"
        f"💰 Цена: <b>{format_price(price)}</b>"
    )
    await cb.message.edit_text(
        text,
        reply_markup=kb_search_product_card(prod_id, page, query),
        parse_mode="HTML"
    )
    await cb.answer()


# ---------- Helper ----------
def _build_results_text(query: str, products, page: int, total: int) -> str:
    lines = [f"🔍 Результаты по запросу «<b>{query}</b>» ({total} шт.):\n"]
    for p in products:
        lines.append(f"• {p['cat_emoji']} <b>{p['name']}</b>")
    return "\n".join(lines)
