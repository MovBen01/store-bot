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
        return FileResponse(webapp_dist / "index.html")

    @app.get("/{path:path}")
    async def serve_app(path: str):
        return FileResponse(webapp_dist / "index.html")
