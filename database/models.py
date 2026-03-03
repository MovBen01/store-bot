from database.db import get_connection


# ─── Users ────────────────────────────────────────────────────────────────────

def get_or_create_user(telegram_id: int, username: str = None, full_name: str = None):
    with get_connection() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        if not user:
            conn.execute(
                "INSERT INTO users (telegram_id, username, full_name) VALUES (?, ?, ?)",
                (telegram_id, username, full_name),
            )
            user = conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            ).fetchone()
        return dict(user)


def update_user_phone(telegram_id: int, phone: str):
    with get_connection() as conn:
        conn.execute("UPDATE users SET phone = ? WHERE telegram_id = ?", (phone, telegram_id))


def update_user_address(telegram_id: int, address: str):
    with get_connection() as conn:
        conn.execute("UPDATE users SET address = ? WHERE telegram_id = ?", (address, telegram_id))


def get_user(telegram_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
        return dict(row) if row else None


def get_all_users():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM users").fetchall()]


# ─── Categories ───────────────────────────────────────────────────────────────

def get_categories(active_only=True):
    with get_connection() as conn:
        q = "SELECT * FROM categories"
        if active_only:
            q += " WHERE is_active = 1"
        return [dict(r) for r in conn.execute(q).fetchall()]


def get_category(cat_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)).fetchone()
        return dict(row) if row else None


def add_category(name: str, description: str = "", emoji: str = "📦"):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO categories (name, description, emoji) VALUES (?, ?, ?)",
            (name, description, emoji),
        )


def delete_category(cat_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE categories SET is_active = 0 WHERE id = ?", (cat_id,))


# ─── Products ─────────────────────────────────────────────────────────────────

def get_products(category_id: int = None, active_only=True):
    with get_connection() as conn:
        q = "SELECT * FROM products WHERE 1=1"
        params = []
        if active_only:
            q += " AND is_active = 1"
        if category_id is not None:
            q += " AND category_id = ?"
            params.append(category_id)
        return [dict(r) for r in conn.execute(q, params).fetchall()]


def get_product(product_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return dict(row) if row else None


def search_products(query: str):
    with get_connection() as conn:
        like = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM products WHERE is_active = 1 AND (name LIKE ? OR description LIKE ?)",
            (like, like),
        ).fetchall()
        return [dict(r) for r in rows]


def add_product(category_id: int, name: str, description: str, price: float,
                photo_id: str = None, stock: int = 0):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO products (category_id, name, description, price, photo_id, stock) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (category_id, name, description, price, photo_id, stock),
        )


def update_product_stock(product_id: int, delta: int):
    with get_connection() as conn:
        conn.execute("UPDATE products SET stock = MAX(0, stock + ?) WHERE id = ?", (delta, product_id))


def delete_product(product_id: int):
    with get_connection() as conn:
        conn.execute("UPDATE products SET is_active = 0 WHERE id = ?", (product_id,))


# ─── Cart ─────────────────────────────────────────────────────────────────────

def get_cart(user_id: int):
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            """
            SELECT c.id, c.quantity, p.id as product_id, p.name, p.price, p.photo_id, p.stock
            FROM cart c
            JOIN products p ON p.id = c.product_id
            WHERE c.user_id = ?
            """,
            (user_id,),
        ).fetchall()]


def add_to_cart(user_id: int, product_id: int, quantity: int = 1):
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE cart SET quantity = quantity + ? WHERE id = ?",
                (quantity, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                (user_id, product_id, quantity),
            )


def remove_from_cart(user_id: int, product_id: int):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM cart WHERE user_id = ? AND product_id = ?",
            (user_id, product_id),
        )


def update_cart_quantity(user_id: int, product_id: int, quantity: int):
    with get_connection() as conn:
        if quantity <= 0:
            conn.execute(
                "DELETE FROM cart WHERE user_id = ? AND product_id = ?",
                (user_id, product_id),
            )
        else:
            conn.execute(
                "UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?",
                (quantity, user_id, product_id),
            )


def clear_cart(user_id: int):
    with get_connection() as conn:
        conn.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))


def get_cart_total(user_id: int) -> float:
    items = get_cart(user_id)
    return sum(i["price"] * i["quantity"] for i in items)


# ─── Orders ───────────────────────────────────────────────────────────────────

def create_order(user_id: int, address: str, comment: str = "") -> int:
    items = get_cart(user_id)
    if not items:
        return 0
    total = sum(i["price"] * i["quantity"] for i in items)
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO orders (user_id, total_price, address, comment) VALUES (?, ?, ?, ?)",
            (user_id, total, address, comment),
        )
        order_id = cur.lastrowid
        for item in items:
            conn.execute(
                "INSERT INTO order_items (order_id, product_id, product_name, quantity, price) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_id, item["product_id"], item["name"], item["quantity"], item["price"]),
            )
    clear_cart(user_id)
    return order_id


def get_orders(user_id: int):
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()]


def get_order(order_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        return dict(row) if row else None


def get_order_items(order_id: int):
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
        ).fetchall()]


def get_all_orders():
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(
            """
            SELECT o.*, u.full_name, u.username, u.telegram_id
            FROM orders o
            JOIN users u ON u.id = o.user_id
            ORDER BY o.created_at DESC
            """
        ).fetchall()]


def update_order_status(order_id: int, status: str):
    with get_connection() as conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))


def get_stats():
    with get_connection() as conn:
        users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        revenue = conn.execute(
            "SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status != 'cancelled'"
        ).fetchone()[0]
        products_count = conn.execute("SELECT COUNT(*) FROM products WHERE is_active = 1").fetchone()[0]
        return {
            "users": users_count,
            "orders": orders_count,
            "revenue": revenue,
            "products": products_count,
        }
