import os
"""
FastAPI server — REST API для WebApp.
Запускается вместе с ботом или отдельно.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import aiosqlite
from pathlib import Path

from config import DB_PATH, ADMIN_IDS
from bot.db.repository import get_setting

app = FastAPI(title="Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def calc_price(base: float) -> float:
    mode = await get_setting("markup_mode") or "percent"
    value = float(await get_setting("markup_value") or "0")
    return round(base * (1 + value / 100)) if mode == "percent" else round(base + value)


# ─── CATEGORIES ───────────────────────────────────────────────
@app.get("/api/categories")
async def get_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, name, emoji FROM categories WHERE visible=1 ORDER BY sort_order") as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


# ─── PRODUCTS ─────────────────────────────────────────────────
@app.get("/api/products")
async def get_products(category_id: Optional[int] = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if category_id:
            q = "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id WHERE p.visible=1 AND p.category_id=? ORDER BY p.id"
            args = (category_id,)
        else:
            q = "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id WHERE p.visible=1 AND c.visible=1 ORDER BY c.sort_order, p.id"
            args = ()
        async with db.execute(q, args) as cur:
            rows = await cur.fetchall()

    result = []
    for r in rows:
        d = dict(r)
        d["display_price"] = await calc_price(d["base_price"])
        result.append(d)
    return result


@app.get("/api/products/search")
async def search_products(q: str = Query(..., min_length=1)):
    like = f"%{q}%"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT p.*, c.name as category_name FROM products p
               JOIN categories c ON p.category_id=c.id
               WHERE p.visible=1 AND c.visible=1
               AND (p.name LIKE ? OR p.description LIKE ? OR c.name LIKE ?)
               ORDER BY c.sort_order, p.id LIMIT 30""",
            (like, like, like)
        ) as cur:
            rows = await cur.fetchall()

    result = []
    for r in rows:
        d = dict(r)
        d["display_price"] = await calc_price(d["base_price"])
        result.append(d)
    return result


@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id WHERE p.id=? AND p.visible=1",
            (product_id,)
        ) as cur:
            row = await cur.fetchone()
    if not row:
        raise HTTPException(404, "Product not found")
    d = dict(row)
    d["display_price"] = await calc_price(d["base_price"])
    return d


# ─── ORDERS ───────────────────────────────────────────────────
class OrderItem(BaseModel):
    product_id: int
    name: str
    price: float
    qty: int

class OrderRequest(BaseModel):
    user_id: int = 0
    username: str = ""
    items: list[OrderItem]
    total: float
    contact: str
    comment: str = ""
    tg_init_data: str = ""

@app.post("/api/orders")
async def create_order(req: OrderRequest):
    from config import BOT_TOKEN, ADMIN_IDS
    import httpx

    # Save each item as separate order row
    order_ids = []
    async with aiosqlite.connect(DB_PATH) as db:
        for item in req.items:
            cur = await db.execute(
                "INSERT INTO orders(user_id, product_id, product_name, price, contact, comment) VALUES(?,?,?,?,?,?)",
                (req.user_id, item.product_id, item.name, item.price * item.qty, req.contact, req.comment)
            )
            order_ids.append(cur.lastrowid)
        await db.commit()

    # Notify admins via Telegram Bot API
    items_text = "\n".join(f"• {i.name} × {i.qty} = {int(i.price*i.qty):,} ₽" for i in req.items)
    msg = (
        f"🛍 <b>Новый заказ из WebApp!</b>\n\n"
        f"{items_text}\n\n"
        f"💰 <b>Итого: {int(req.total):,} ₽</b>\n"
        f"📞 Контакт: {req.contact}\n"
        f"👤 @{req.username or 'неизвестно'}\n"
        f"💬 {req.comment or '—'}"
    )
    async with httpx.AsyncClient() as client:
        for admin_id in ADMIN_IDS:
            try:
                await client.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": admin_id, "text": msg, "parse_mode": "HTML"}
                )
            except Exception:
                pass

    return {"ok": True, "order_ids": order_ids}


# ─── SERVE REACT BUILD ────────────────────────────────────────
webapp_dist = Path(__file__).parent.parent / "webapp" / "dist"
if webapp_dist.exists():
    app.mount("/assets", StaticFiles(directory=webapp_dist / "assets"), name="assets")

@app.get("/")
async def serve_index():
    index = Path(__file__).parent.parent / "webapp" / "dist" / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"status": "API running"}


# ════════════════════════════════════════════════
# ADMIN API  (защищено токеном)
# ════════════════════════════════════════════════
import hashlib, secrets
from fastapi import Header, HTTPException as FastHTTPException
from pydantic import BaseModel as BM

ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "changeme123")
_sessions: set[str] = set()

def _check(x_admin_token: str = Header(default="")):
    if x_admin_token not in _sessions:
        raise FastHTTPException(status_code=401, detail="Unauthorized")

class LoginReq(BM):
    password: str

@app.post("/admin-api/login")
async def admin_login(req: LoginReq):
    if req.password != ADMIN_SECRET:
        raise FastHTTPException(status_code=401, detail="Wrong password")
    token = secrets.token_hex(32)
    _sessions.add(token)
    return {"token": token}

@app.get("/admin-api/stats")
async def admin_stats(x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT COUNT(*) as n FROM orders") as c: total = (await c.fetchone())["n"]
        async with db.execute("SELECT COUNT(*) as n FROM orders WHERE status='new'") as c: new_ = (await c.fetchone())["n"]
        async with db.execute("SELECT COALESCE(SUM(price),0) as s FROM orders WHERE status='done'") as c: rev = (await c.fetchone())["s"]
        async with db.execute("SELECT COUNT(*) as n FROM products WHERE visible=1") as c: prods = (await c.fetchone())["n"]
        async with db.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 10") as c: recent = [dict(r) for r in await c.fetchall()]
    return {"orders_total": total, "orders_new": new_, "revenue": rev, "products_count": prods, "recent_orders": recent}

# --- Categories ---
class CatBody(BM):
    name: str; emoji: str = "📦"; sort_order: int = 0; visible: int = 1

@app.get("/admin-api/categories")
async def adm_get_cats(x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM categories ORDER BY sort_order") as c:
            return [dict(r) for r in await c.fetchall()]

@app.post("/admin-api/categories")
async def adm_create_cat(body: CatBody, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO categories(name,emoji,sort_order,visible) VALUES(?,?,?,?)",
            (body.name, body.emoji, body.sort_order, body.visible))
        await db.commit()
    return {"ok": True}

@app.put("/admin-api/categories/{cat_id}")
async def adm_update_cat(cat_id: int, body: CatBody, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE categories SET name=?,emoji=?,sort_order=?,visible=? WHERE id=?",
            (body.name, body.emoji, body.sort_order, body.visible, cat_id))
        await db.commit()
    return {"ok": True}

@app.delete("/admin-api/categories/{cat_id}")
async def adm_del_cat(cat_id: int, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        await db.commit()
    return {"ok": True}

# --- Products ---
class ProdBody(BM):
    name: str; sku: str = ""; description: str = ""
    base_price: float; category_id: int; visible: int = 1

@app.get("/admin-api/products")
async def adm_get_prods(x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT p.*, c.name as cat_name FROM products p LEFT JOIN categories c ON p.category_id=c.id ORDER BY c.sort_order, p.id") as c:
            return [dict(r) for r in await c.fetchall()]

@app.post("/admin-api/products")
async def adm_create_prod(body: ProdBody, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    sku = body.sku or body.name.lower().replace(" ","-")[:30] + "-" + str(int(__import__("time").time()))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO products(name,sku,description,base_price,category_id,visible) VALUES(?,?,?,?,?,?)",
            (body.name, sku, body.description, body.base_price, body.category_id, body.visible))
        await db.commit()
    return {"ok": True}

@app.put("/admin-api/products/{prod_id}")
async def adm_update_prod(prod_id: int, body: ProdBody, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET name=?,description=?,base_price=?,category_id=?,visible=? WHERE id=?",
            (body.name, body.description, body.base_price, body.category_id, body.visible, prod_id))
        await db.commit()
    return {"ok": True}

@app.delete("/admin-api/products/{prod_id}")
async def adm_del_prod(prod_id: int, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id=?", (prod_id,))
        await db.commit()
    return {"ok": True}

# --- Orders ---
class StatusBody(BM):
    status: str

@app.get("/admin-api/orders")
async def adm_get_orders(x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 100") as c:
            return [dict(r) for r in await c.fetchall()]

@app.put("/admin-api/orders/{order_id}/status")
async def adm_order_status(order_id: int, body: StatusBody, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?", (body.status, order_id))
        await db.commit()
    return {"ok": True}

# --- Settings ---
@app.get("/admin-api/settings")
async def adm_get_settings(x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT key, value FROM settings") as c:
            rows = await c.fetchall()
    return {r["key"]: r["value"] for r in rows}

class SettingsBody(BM):
    markup_mode: str; markup_value: str

@app.put("/admin-api/settings")
async def adm_update_settings(body: SettingsBody, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('markup_mode',?)", (body.markup_mode,))
        await db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('markup_value',?)", (body.markup_value,))
        await db.commit()
    return {"ok": True}


# ─── SERVE ADMIN BUILD ────────────────────────────────────────
admin_dist = Path(__file__).parent.parent / "webapp_admin" / "dist"
if admin_dist.exists():
    app.mount("/admin-assets", StaticFiles(directory=admin_dist / "assets"), name="admin-assets")

# ─── SMART CATCH-ALL (must be LAST) ──────────────────────────
@app.get("/{path:path}")
async def catch_all(path: str):
    # Admin routes
    if path.startswith("admin"):
        index = Path(__file__).parent.parent / "webapp_admin" / "dist" / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"error": "Admin build not found. Run: cd webapp_admin && npm run build"}
    # Main webapp
    index = Path(__file__).parent.parent / "webapp" / "dist" / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"status": "API running, webapp not built"}
