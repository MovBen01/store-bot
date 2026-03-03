import aiosqlite
from config import DB_PATH
from typing import Optional


async def get_db():
    return aiosqlite.connect(DB_PATH)


# ---------- Settings ----------
async def get_setting(key: str) -> Optional[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key=?", (key,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else None


async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
        await db.commit()


# ---------- Users ----------
async def upsert_user(user_id: int, username: str, full_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO users(id, username, full_name) VALUES(?,?,?)",
            (user_id, username, full_name),
        )
        await db.commit()


# ---------- Categories ----------
async def get_categories(only_visible: bool = True):
    q = "SELECT id, name, emoji FROM categories"
    if only_visible:
        q += " WHERE visible=1"
    q += " ORDER BY sort_order"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(q) as cur:
            return await cur.fetchall()


async def get_all_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, name, emoji, visible FROM categories ORDER BY sort_order") as cur:
            return await cur.fetchall()


async def set_category_visible(cat_id: int, visible: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE categories SET visible=? WHERE id=?", (int(visible), cat_id))
        await db.commit()


# ---------- Products ----------
async def get_products(category_id: int, only_visible: bool = True):
    q = "SELECT id, sku, name, description, base_price FROM products WHERE category_id=?"
    if only_visible:
        q += " AND visible=1"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(q, (category_id,)) as cur:
            return await cur.fetchall()


async def get_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, sku, name, description, base_price, visible FROM products WHERE id=?",
            (product_id,),
        ) as cur:
            return await cur.fetchone()


async def get_all_products():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT p.id, p.name, p.base_price, p.visible, c.name as cat_name "
            "FROM products p JOIN categories c ON p.category_id=c.id ORDER BY c.sort_order, p.id"
        ) as cur:
            return await cur.fetchall()


async def set_product_visible(prod_id: int, visible: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET visible=? WHERE id=?", (int(visible), prod_id))
        await db.commit()


async def update_product_price(sku: str, price: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET base_price=? WHERE sku=?", (price, sku))
        await db.commit()


# ---------- Orders ----------
async def create_order(user_id, product_id, product_name, price, contact, comment) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO orders(user_id, product_id, product_name, price, contact, comment) VALUES(?,?,?,?,?,?)",
            (user_id, product_id, product_name, price, contact, comment),
        )
        await db.commit()
        return cur.lastrowid


async def get_recent_orders(limit: int = 20):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT o.id, o.product_name, o.price, o.contact, o.comment, o.status, o.created_at, u.username "
            "FROM orders o LEFT JOIN users u ON o.user_id=u.id "
            "ORDER BY o.created_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            return await cur.fetchall()


async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM orders WHERE id=?", (order_id,)) as cur:
            return await cur.fetchone()


async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
        await db.commit()


# ---------- Search ----------
async def search_products(query: str, limit: int = 20, offset: int = 0):
    q = query.strip()
    like = f"%{q}%"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT p.id, p.name, p.description, p.base_price, c.name as cat_name, c.emoji as cat_emoji
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.visible=1 AND c.visible=1
              AND (p.name LIKE ? OR p.description LIKE ? OR c.name LIKE ?)
            ORDER BY c.sort_order, p.id
            LIMIT ? OFFSET ?
            """,
            (like, like, like, limit, offset)
        ) as cur:
            return await cur.fetchall()


async def count_search_results(query: str) -> int:
    like = f"%{query.strip()}%"
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT COUNT(*) FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.visible=1 AND c.visible=1
              AND (p.name LIKE ? OR p.description LIKE ? OR c.name LIKE ?)
            """,
            (like, like, like)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0
