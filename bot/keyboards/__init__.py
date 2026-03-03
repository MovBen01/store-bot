from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def kb_main_menu() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog"),
          InlineKeyboardButton(text="🔍 Поиск", callback_data="search"))
    b.row(InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders"))
    b.row(InlineKeyboardButton(text="💬 Поддержка", callback_data="support"),
          InlineKeyboardButton(text="❓ FAQ", callback_data="faq"))
    return b.as_markup()


def kb_categories(categories) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for cat in categories:
        b.row(InlineKeyboardButton(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"cat:{cat['id']}"
        ))
    b.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu"))
    return b.as_markup()


def kb_products(products) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        b.row(InlineKeyboardButton(text=p["name"], callback_data=f"prod:{p['id']}"))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="catalog"))
    return b.as_markup()


def kb_product_card(product_id: int, cat_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy:{product_id}"))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data=f"cat:{cat_id}"))
    return b.as_markup()


def kb_cancel_order() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order"))
    return b.as_markup()


def kb_confirm_order() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order"),
          InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_order"))
    return b.as_markup()


def kb_back_main() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data="main_menu"))
    return b.as_markup()


# ---- ADMIN ----
def kb_admin_main() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="💰 Наценка", callback_data="adm:markup"))
    b.row(InlineKeyboardButton(text="🔄 Обновить каталог", callback_data="adm:refresh"))
    b.row(InlineKeyboardButton(text="📦 Товары/Категории", callback_data="adm:products"))
    b.row(InlineKeyboardButton(text="📋 Последние заказы", callback_data="adm:orders"))
    b.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"))
    return b.as_markup()


def kb_admin_markup() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="% Процент", callback_data="adm:markup_mode:percent"),
          InlineKeyboardButton(text="₽ Фиксированная", callback_data="adm:markup_mode:fixed"))
    b.row(InlineKeyboardButton(text="✏️ Изменить значение", callback_data="adm:markup_edit"))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="adm:back"))
    return b.as_markup()


def kb_admin_products(categories, products) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="── Категории ──", callback_data="noop"))
    for cat in categories:
        status = "✅" if cat["visible"] else "❌"
        b.row(InlineKeyboardButton(
            text=f"{status} {cat['emoji']} {cat['name']}",
            callback_data=f"adm:toggle_cat:{cat['id']}"
        ))
    b.row(InlineKeyboardButton(text="── Товары ──", callback_data="noop"))
    for p in products:
        status = "✅" if p["visible"] else "❌"
        b.row(InlineKeyboardButton(
            text=f"{status} {p['name']} ({p['cat_name']})",
            callback_data=f"adm:toggle_prod:{p['id']}"
        ))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="adm:back"))
    return b.as_markup()


def kb_admin_orders(orders) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for o in orders:
        b.row(InlineKeyboardButton(
            text=f"#{o['id']} {o['product_name'][:20]} — {o['status']}",
            callback_data=f"adm:order:{o['id']}"
        ))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="adm:back"))
    return b.as_markup()


def kb_admin_order_detail(order_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Выполнен", callback_data=f"adm:order_status:{order_id}:done"),
          InlineKeyboardButton(text="❌ Отменён", callback_data=f"adm:order_status:{order_id}:cancelled"))
    b.row(InlineKeyboardButton(text="◀️ Назад", callback_data="adm:orders"))
    return b.as_markup()


# ---- SEARCH ----
SEARCH_PAGE_SIZE = 5


def kb_search_results(products, query: str, page: int, total: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in products:
        b.row(InlineKeyboardButton(
            text=f"{p['cat_emoji']} {p['name']}",
            callback_data=f"search_prod:{p['id']}:{page}:{query[:20]}"
        ))
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"search_page:{page-1}:{query[:20]}"))
    pages = (total - 1) // SEARCH_PAGE_SIZE + 1
    nav.append(InlineKeyboardButton(text=f"{page+1}/{pages}", callback_data="noop"))
    if (page + 1) * SEARCH_PAGE_SIZE < total:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"search_page:{page+1}:{query[:20]}"))
    if nav:
        b.row(*nav)
    b.row(InlineKeyboardButton(text="🔍 Новый поиск", callback_data="search"),
          InlineKeyboardButton(text="◀️ Меню", callback_data="main_menu"))
    return b.as_markup()


def kb_search_product_card(product_id: int, page: int, query: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🛒 Купить", callback_data=f"buy:{product_id}"))
    b.row(InlineKeyboardButton(text="◀️ К результатам", callback_data=f"search_page:{page}:{query[:20]}"))
    return b.as_markup()


def kb_search_empty() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔍 Попробовать снова", callback_data="search"))
    b.row(InlineKeyboardButton(text="🛍 Весь каталог", callback_data="catalog"),
          InlineKeyboardButton(text="◀️ Меню", callback_data="main_menu"))
    return b.as_markup()
