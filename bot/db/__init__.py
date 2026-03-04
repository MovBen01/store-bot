import aiosqlite
from config import DB_PATH

CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    full_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    emoji TEXT DEFAULT '',
    visible INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0,
    image_url TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(id),
    sku TEXT UNIQUE,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    base_price REAL DEFAULT 0,
    visible INTEGER DEFAULT 1,
    image_url TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product_id INTEGER,
    product_name TEXT,
    price REAL,
    contact TEXT,
    comment TEXT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS catalog_cache (
    sku TEXT PRIMARY KEY,
    name TEXT,
    category TEXT,
    description TEXT,
    raw_price REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

SEED_DATA = """
INSERT OR IGNORE INTO settings(key, value) VALUES('markup_mode', 'percent');
INSERT OR IGNORE INTO settings(key, value) VALUES('markup_value', '10');
INSERT OR IGNORE INTO categories(id, name, emoji, sort_order) VALUES(1, 'iPhone', '📱', 1);
INSERT OR IGNORE INTO categories(id, name, emoji, sort_order) VALUES(2, 'MacBook', '💻', 2);
INSERT OR IGNORE INTO categories(id, name, emoji, sort_order) VALUES(3, 'iPad', '🗂', 3);
INSERT OR IGNORE INTO categories(id, name, emoji, sort_order) VALUES(4, 'AirPods', '🎧', 4);
INSERT OR IGNORE INTO categories(id, name, emoji, sort_order) VALUES(5, 'Apple Watch', '⌚', 5);
INSERT OR IGNORE INTO settings(key, value) VALUES('design_accent_color', '#f97316');
INSERT OR IGNORE INTO settings(key, value) VALUES('design_bg_color', '#0a0a0a');
INSERT OR IGNORE INTO settings(key, value) VALUES('design_store_name', 'Apple Store');
INSERT OR IGNORE INTO settings(key, value) VALUES('design_hero_title', 'iPhone 16 Pro\nУже в наличии');
INSERT OR IGNORE INTO settings(key, value) VALUES('design_hero_subtitle', 'Титановый корпус. Чип A18 Pro.');
INSERT OR IGNORE INTO settings(key, value) VALUES('design_support_text', 'По всем вопросам: @support_username');
INSERT OR IGNORE INTO settings(key, value) VALUES('design_show_hero', '1');

INSERT OR IGNORE INTO products(category_id, sku, name, description, base_price) VALUES
  (1, 'iphone16-128', 'iPhone 16 128GB', 'Новейший iPhone 16, 128 ГБ, различные цвета', 89990),
  (1, 'iphone16-256', 'iPhone 16 256GB', 'Новейший iPhone 16, 256 ГБ, различные цвета', 99990),
  (1, 'iphone16pro-256', 'iPhone 16 Pro 256GB', 'iPhone 16 Pro, 256 ГБ, титан', 119990),
  (2, 'macbook-air-m3', 'MacBook Air M3 13"', 'MacBook Air с чипом M3, 8/256 ГБ', 129990),
  (2, 'macbook-pro-m4', 'MacBook Pro M4 14"', 'MacBook Pro с чипом M4, 16/512 ГБ', 199990),
  (3, 'ipad-air-11', 'iPad Air 11" M2', 'iPad Air M2, 128 ГБ, Wi-Fi', 79990),
  (4, 'airpods-4', 'AirPods 4', 'AirPods 4 с активным шумоподавлением', 19990),
  (4, 'airpods-pro-2', 'AirPods Pro 2', 'AirPods Pro 2-го поколения', 24990),
  (5, 'watch-s10-41', 'Apple Watch Series 10 41mm', 'Apple Watch Series 10, 41 мм, алюминий', 39990);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(CREATE_TABLES)
        await db.executescript(SEED_DATA)
        # Safe migrations for existing DBs
        for sql in [
            "ALTER TABLE categories ADD COLUMN image_url TEXT DEFAULT ''",
            "ALTER TABLE products ADD COLUMN image_url TEXT DEFAULT ''",
        ]:
            try:
                await db.execute(sql)
            except Exception:
                pass  # Column already exists
        await db.commit()
