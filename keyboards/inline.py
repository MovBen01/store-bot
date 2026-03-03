from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def categories_kb(categories: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"{c['emoji']} {c['name']}", callback_data=f"cat_{c['id']}")]
        for c in categories
    ]
    return InlineKeyboardMarkup(buttons)


def products_kb(products: list, page: int, total_pages: int, cat_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"🔸 {p['name']} — {p['price']:.0f}₽", callback_data=f"prod_{p['id']}")]
        for p in products
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"ppage_{cat_id}_{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"ppage_{cat_id}_{page + 1}"))
    if nav:
        buttons.append(nav)
    buttons.append([InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_cats")])
    return InlineKeyboardMarkup(buttons)


def product_detail_kb(product_id: int, cat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 В корзину", callback_data=f"addcart_{product_id}")],
        [InlineKeyboardButton("🔙 Назад", callback_data=f"cat_{cat_id}")],
    ])


def cart_kb(items: list) -> InlineKeyboardMarkup:
    buttons = []
    for item in items:
        buttons.append([
            InlineKeyboardButton(f"➖", callback_data=f"cartdec_{item['product_id']}"),
            InlineKeyboardButton(
                f"{item['name']} x{item['quantity']}",
                callback_data="noop"
            ),
            InlineKeyboardButton(f"➕", callback_data=f"cartinc_{item['product_id']}"),
            InlineKeyboardButton("🗑", callback_data=f"cartdel_{item['product_id']}"),
        ])
    buttons.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
    buttons.append([InlineKeyboardButton("🗑 Очистить корзину", callback_data="clearcart")])
    return InlineKeyboardMarkup(buttons)


def order_status_kb(order_id: int) -> InlineKeyboardMarkup:
    statuses = [
        ("✅ Подтверждён", "confirmed"),
        ("🔧 В обработке", "processing"),
        ("🚚 Отправлен", "shipped"),
        ("📦 Доставлен", "delivered"),
        ("❌ Отменён", "cancelled"),
    ]
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"setstatus_{order_id}_{status}")]
        for label, status in statuses
    ]
    return InlineKeyboardMarkup(buttons)


def orders_list_kb(orders: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            f"#{o['id']} — {o['total_price']:.0f}₽ ({o['status']})",
            callback_data=f"order_{o['id']}"
        )]
        for o in orders
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"ordpage_{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"ordpage_{page + 1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(buttons)


def admin_orders_kb(orders: list, page: int, total_pages: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            f"#{o['id']} {o['full_name'] or o['username'] or 'Аноним'} — {o['total_price']:.0f}₽",
            callback_data=f"adminorder_{o['id']}"
        )]
        for o in orders
    ]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️", callback_data=f"aordpage_{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("▶️", callback_data=f"aordpage_{page + 1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(buttons)


def delete_products_kb(products: list) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"🗑 {p['name']} — {p['price']:.0f}₽", callback_data=f"delprod_{p['id']}")]
        for p in products
    ]
    return InlineKeyboardMarkup(buttons)
