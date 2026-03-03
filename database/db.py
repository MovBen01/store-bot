import sqlite3
from config import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username    TEXT,
                full_name   TEXT,
                phone       TEXT,
                address     TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL,
                description TEXT,
                emoji       TEXT DEFAULT '📦',
                is_active   INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS products (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                name        TEXT NOT NULL,
                description TEXT,
                price       REAL NOT NULL,
                photo_id    TEXT,
                stock       INTEGER DEFAULT 0,
                is_active   INTEGER DEFAULT 1,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS cart (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                quantity    INTEGER DEFAULT 1,
                UNIQUE(user_id, product_id)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                total_price REAL NOT NULL,
                status      TEXT DEFAULT 'pending',
                address     TEXT,
                comment     TEXT,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_id  INTEGER REFERENCES products(id),
                product_name TEXT NOT NULL,
                quantity    INTEGER NOT NULL,
                price       REAL NOT NULL
            );
        """)
