import os
import sys
import secrets
import re as _re
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import aiosqlite
from pathlib import Path

from config import DB_PATH, ADMIN_IDS

ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "changeme123")
_sessions: set[str] = set()

app = FastAPI(title="Shop API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Paths ──────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.parent
WEBAPP_DIST = ROOT / "webapp"      / "dist"
ADMIN_DIST  = ROOT / "webapp_admin"/ "dist"

# ── Mount static assets FIRST (most specific wins) ─────────────
if (WEBAPP_DIST / "assets").exists():
    app.mount("/assets",       StaticFiles(directory=WEBAPP_DIST / "assets"),      name="webapp-assets")

if (ADMIN_DIST / "assets").exists():
    app.mount("/admin/assets", StaticFiles(directory=ADMIN_DIST  / "assets"),      name="admin-assets")


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
async def get_setting(key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key=?", (key,)) as c:
            row = await c.fetchone()
            return row[0] if row else None

async def calc_price(base: float) -> float:
    mode  = await get_setting("markup_mode")  or "percent"
    value = float(await get_setting("markup_value") or "0")
    return round(base * (1 + value / 100)) if mode == "percent" else round(base + value)

def _auth(token: str):
    if token not in _sessions:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ══════════════════════════════════════════════════════════════
# PUBLIC API  /api/*
# ══════════════════════════════════════════════════════════════
@app.get("/api/categories")
async def get_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id,name,emoji FROM categories WHERE visible=1 ORDER BY sort_order") as c:
            return [dict(r) for r in await c.fetchall()]

@app.get("/api/products")
async def get_products(category_id: Optional[int] = None):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        if category_id:
            sql  = "SELECT p.*,c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id WHERE p.visible=1 AND p.category_id=? ORDER BY p.id"
            args = (category_id,)
        else:
            sql  = "SELECT p.*,c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id WHERE p.visible=1 AND c.visible=1 ORDER BY c.sort_order,p.id"
            args = ()
        async with db.execute(sql, args) as c:
            rows = await c.fetchall()
    result = []
    for r in rows:
        d = dict(r); d["display_price"] = await calc_price(d["base_price"]); result.append(d)
    return result

@app.get("/api/products/search")
async def search_products(q: str = Query(..., min_length=1)):
    like = f"%{q}%"
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT p.*,c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id "
            "WHERE p.visible=1 AND c.visible=1 AND (p.name LIKE ? OR p.description LIKE ? OR c.name LIKE ?) "
            "ORDER BY c.sort_order,p.id LIMIT 30", (like,like,like)
        ) as c: rows = await c.fetchall()
    result = []
    for r in rows:
        d = dict(r); d["display_price"] = await calc_price(d["base_price"]); result.append(d)
    return result

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT p.*,c.name as category_name FROM products p JOIN categories c ON p.category_id=c.id WHERE p.id=? AND p.visible=1",
            (product_id,)
        ) as c: row = await c.fetchone()
    if not row: raise HTTPException(404, "Not found")
    d = dict(row); d["display_price"] = await calc_price(d["base_price"]); return d

class OrderItem(BaseModel):
    product_id: int; name: str; price: float; qty: int

class OrderRequest(BaseModel):
    user_id: int = 0; username: str = ""; items: list[OrderItem]
    total: float; contact: str; comment: str = ""; tg_init_data: str = ""

@app.post("/api/orders")
async def create_order(req: OrderRequest):
    import httpx
    order_ids = []
    async with aiosqlite.connect(DB_PATH) as db:
        for item in req.items:
            cur = await db.execute(
                "INSERT INTO orders(user_id,product_id,product_name,price,contact,comment) VALUES(?,?,?,?,?,?)",
                (req.user_id, item.product_id, item.name, item.price*item.qty, req.contact, req.comment)
            )
            order_ids.append(cur.lastrowid)
        await db.commit()
    items_text = "\n".join(f"• {i.name} × {i.qty} = {int(i.price*i.qty):,} ₽" for i in req.items)
    msg = f"🛍 <b>Новый заказ из WebApp!</b>\n\n{items_text}\n\n💰 <b>Итого: {int(req.total):,} ₽</b>\n📞 {req.contact}\n👤 @{req.username or '—'}\n💬 {req.comment or '—'}"
    from config import BOT_TOKEN
    async with httpx.AsyncClient() as client:
        for aid in ADMIN_IDS:
            try: await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":aid,"text":msg,"parse_mode":"HTML"})
            except: pass
    return {"ok": True, "order_ids": order_ids}


# ══════════════════════════════════════════════════════════════
# ADMIN API  /admin-api/*
# ══════════════════════════════════════════════════════════════
class LoginReq(BaseModel):
    password: str

@app.post("/admin-api/login")
async def admin_login(req: LoginReq):
    if req.password != ADMIN_SECRET:
        raise HTTPException(401, "Wrong password")
    token = secrets.token_hex(32)
    _sessions.add(token)
    return {"token": token}

@app.get("/admin-api/stats")
async def admin_stats(x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT COUNT(*) n FROM orders") as c: total = (await c.fetchone())["n"]
        async with db.execute("SELECT COUNT(*) n FROM orders WHERE status='new'") as c: new_ = (await c.fetchone())["n"]
        async with db.execute("SELECT COALESCE(SUM(price),0) s FROM orders WHERE status='done'") as c: rev = (await c.fetchone())["s"]
        async with db.execute("SELECT COUNT(*) n FROM products WHERE visible=1") as c: prods = (await c.fetchone())["n"]
        async with db.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 10") as c: recent = [dict(r) for r in await c.fetchall()]
    return {"orders_total":total,"orders_new":new_,"revenue":rev,"products_count":prods,"recent_orders":recent}

class CatBody(BaseModel):
    name: str; emoji: str = "📦"; sort_order: int = 0; visible: int = 1; image_url: str = ""

@app.get("/admin-api/categories")
async def adm_cats(x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM categories ORDER BY sort_order") as c:
            return [dict(r) for r in await c.fetchall()]

@app.post("/admin-api/categories")
async def adm_create_cat(body: CatBody, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO categories(name,emoji,sort_order,visible,image_url) VALUES(?,?,?,?,?)",(body.name,body.emoji,body.sort_order,body.visible,body.image_url))
        await db.commit()
    return {"ok":True}

@app.put("/admin-api/categories/{cat_id}")
async def adm_upd_cat(cat_id: int, body: CatBody, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE categories SET name=?,emoji=?,sort_order=?,visible=?,image_url=? WHERE id=?",(body.name,body.emoji,body.sort_order,body.visible,body.image_url,cat_id))
        await db.commit()
    return {"ok":True}

@app.delete("/admin-api/categories/{cat_id}")
async def adm_del_cat(cat_id: int, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM categories WHERE id=?",(cat_id,)); await db.commit()
    return {"ok":True}

class ProdBody(BaseModel):
    name: str; sku: str = ""; description: str = ""; base_price: float; category_id: int; visible: int = 1; image_url: str = ""

@app.get("/admin-api/products")
async def adm_prods(x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT p.*,c.name as cat_name FROM products p LEFT JOIN categories c ON p.category_id=c.id ORDER BY c.sort_order,p.id") as c:
            return [dict(r) for r in await c.fetchall()]

@app.post("/admin-api/products")
async def adm_create_prod(body: ProdBody, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    import time
    sku = body.sku or body.name.lower().replace(" ","-")[:30]+"-"+str(int(time.time()))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO products(name,sku,description,base_price,category_id,visible,image_url) VALUES(?,?,?,?,?,?,?)",(body.name,sku,body.description,body.base_price,body.category_id,body.visible,body.image_url))
        await db.commit()
    return {"ok":True}

@app.put("/admin-api/products/{prod_id}")
async def adm_upd_prod(prod_id: int, body: ProdBody, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET name=?,description=?,base_price=?,category_id=?,visible=?,image_url=? WHERE id=?",(body.name,body.description,body.base_price,body.category_id,body.visible,body.image_url,prod_id))
        await db.commit()
    return {"ok":True}

@app.delete("/admin-api/products/{prod_id}")
async def adm_del_prod(prod_id: int, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id=?",(prod_id,)); await db.commit()
    return {"ok":True}

class StatusBody(BaseModel):
    status: str

@app.get("/admin-api/orders")
async def adm_orders(x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 100") as c:
            return [dict(r) for r in await c.fetchall()]

@app.put("/admin-api/orders/{order_id}/status")
async def adm_order_status(order_id: int, body: StatusBody, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status=? WHERE id=?",(body.status,order_id)); await db.commit()
    return {"ok":True}

@app.get("/admin-api/settings")
async def adm_settings(x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT key,value FROM settings") as c:
            return {r["key"]:r["value"] for r in await c.fetchall()}

class SettingsBody(BaseModel):
    markup_mode: str; markup_value: str

@app.put("/admin-api/settings")
async def adm_upd_settings(body: SettingsBody, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('markup_mode',?)",(body.markup_mode,))
        await db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('markup_value',?)",(body.markup_value,))
        await db.commit()
    return {"ok":True}



# ══════════════════════════════════════════════════════════════
# DESIGN API  /admin-api/design
# ══════════════════════════════════════════════════════════════
DESIGN_KEYS = [
    "design_accent_color", "design_bg_color", "design_store_name",
    "design_hero_title", "design_hero_subtitle", "design_support_text",
    "design_show_hero",
]

@app.get("/admin-api/design")
async def adm_get_design(x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT key,value FROM settings WHERE key LIKE 'design_%'") as c:
            return {r["key"]: r["value"] for r in await c.fetchall()}

class DesignBody(BaseModel):
    design_accent_color: str = "#f97316"
    design_bg_color: str = "#0a0a0a"
    design_store_name: str = "Apple Store"
    design_hero_title: str = "iPhone 16 Pro"
    design_hero_subtitle: str = "Титановый корпус. Чип A18 Pro."
    design_support_text: str = "По всем вопросам: @support_username"
    design_show_hero: str = "1"

@app.put("/admin-api/design")
async def adm_upd_design(body: DesignBody, x_admin_token: str = Header(default="")):
    _auth(x_admin_token)
    async with aiosqlite.connect(DB_PATH) as db:
        for key in DESIGN_KEYS:
            val = getattr(body, key, "")
            await db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, val))
        await db.commit()
    return {"ok": True}

# Public design endpoint (no auth — webapp needs it)
@app.get("/api/design")
async def get_design():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT key,value FROM settings WHERE key LIKE 'design_%'") as c:
            return {r["key"]: r["value"] for r in await c.fetchall()}

# ══════════════════════════════════════════════════════════════
# HTML PAGES  (must come AFTER all API routes)
# ══════════════════════════════════════════════════════════════
@app.get("/admin")
@app.get("/admin/")
async def serve_admin_index():
    f = ADMIN_DIST / "index.html"
    return FileResponse(f) if f.exists() else JSONResponse({"error":"Admin not built"}, 503)

@app.get("/")
async def serve_index():
    f = WEBAPP_DIST / "index.html"
    return FileResponse(f) if f.exists() else JSONResponse({"status":"API running"})

# This must be absolutely last — catches everything else for SPA routing
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if full_path.startswith("admin"):
        f = ADMIN_DIST / "index.html"
        return FileResponse(f) if f.exists() else JSONResponse({"error":"Admin not built"}, 503)
    f = WEBAPP_DIST / "index.html"
    return FileResponse(f) if f.exists() else JSONResponse({"status":"API running"})
