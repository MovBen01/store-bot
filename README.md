<<<<<<< HEAD
# 🍎 Apple Shop Telegram Bot

Telegram-бот "магазин Apple-техники" на aiogram v3.
=======
# 🛍 Telegram Store Bot

Полноценный магазин-бот для Telegram на Python.

## Возможности

- 🛍 Каталог товаров с категориями и фото
- 🔍 Поиск товаров
- 🛒 Корзина с управлением количеством
- 📦 История заказов с отслеживанием статуса
- 👤 Профиль пользователя (телефон, адрес)
- 🔧 Админ-панель:
  - Добавление/удаление категорий и товаров
  - Просмотр всех заказов
  - Изменение статуса заказов (с уведомлением клиента)
  - Статистика (пользователи, заказы, выручка)
  - Рассылка всем пользователям

## Установка

### 1. Получить токен бота

Напишите [@BotFather](https://t.me/BotFather) в Telegram:
```
/newbot
```
Скопируйте полученный токен.

### 2. Настроить .env

Откройте файл `.env` и вставьте ваши данные:
```
BOT_TOKEN=ВАШ_ТОКЕН_ЗДЕСЬ
ADMIN_IDS=ВАШ_TELEGRAM_ID
```

Узнать свой Telegram ID можно через [@userinfobot](https://t.me/userinfobot).

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Запустить бота

```bash
python bot.py
```
>>>>>>> a3f6ff9e60154a5b9e6d149779d7bbcc564473b9

## Структура проекта

```
<<<<<<< HEAD
shop_bot/
├── main.py                   # Точка входа
├── config.py                 # Настройки из .env
├── requirements.txt
├── .env.example
├── bot/
│   ├── db/
│   │   ├── __init__.py       # Инициализация БД + таблицы
│   │   └── repository.py     # Все запросы к БД
│   ├── handlers/
│   │   ├── user/
│   │   │   ├── menu.py       # Каталог, категории, товары, FAQ
│   │   │   └── order.py      # FSM оформления заказа
│   │   └── admin/
│   │       └── panel.py      # Админ-панель
│   ├── keyboards/
│   │   └── __init__.py       # Все inline-клавиатуры
│   └── services/
│       └── pricing.py        # PriceCalculator + провайдеры
└── userbot/
    └── bigsale_provider.py   # Опциональный Telethon-провайдер
```

## Установка (Windows PowerShell)

```powershell
# 1. Клонировать / скопировать папку shop_bot
cd shop_bot

# 2. Создать виртуальное окружение
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env файл
Copy-Item .env.example .env
notepad .env   # заполнить BOT_TOKEN и ADMIN_IDS

# 5. Запустить бота
python main.py
```

## Настройка .env

| Переменная | Описание | Пример |
|---|---|---|
| `BOT_TOKEN` | Токен бота от @BotFather | `123456:ABC...` |
| `ADMIN_IDS` | ID админов через запятую | `123456789,987654321` |
| `PRICE_PROVIDER` | `mock` или `userbot` | `mock` |
| `MARKUP_MODE` | `percent` или `fixed` | `percent` |
| `MARKUP_VALUE` | Значение наценки | `10` |
| `DB_PATH` | Путь к SQLite БД | `shop.db` |

## Добавить администратора

1. Узнайте свой Telegram ID у @userinfobot
2. Добавьте в `.env`:  `ADMIN_IDS=ВАШ_ID`
3. Перезапустите бота
4. Откройте бота и напишите `/admin`

## Провайдеры цен

### Mock (по умолчанию)
Использует цены из локальной БД. Идеально для старта.
```
PRICE_PROVIDER=mock
```

### Userbot (BigSaleApple)
⚠️ **ВНИМАНИЕ**: Использование userbot может нарушать Telegram ToS.
Используйте только в ознакомительных целях и только со своим аккаунтом.

```
PRICE_PROVIDER=userbot
USERBOT_API_ID=12345678
USERBOT_API_HASH=abcdef1234567890
USERBOT_SESSION=my_session
BIGSALE_BOT_USERNAME=BigSaleApple
```

Дополнительно установите: `pip install telethon`

При первом запуске Telethon попросит авторизоваться через номер телефона.

## Управление наценкой (Admin)

Войдите в `/admin` → 💰 Наценка:
- **Процент** — цена × (1 + N/100)
- **Фиксированная** — цена + N рублей

## Команды

| Команда | Описание |
|---|---|
| `/start` | Главное меню магазина |
| `/admin` | Панель администратора |

## Технологии

- Python 3.11+
- aiogram 3.x
- aiosqlite (SQLite)
- Опционально: Telethon
=======
store_bot/
├── bot.py              # Точка входа
├── config.py           # Настройки
├── .env                # Токен и ID администраторов
├── requirements.txt
├── database/
│   ├── db.py           # Подключение и инициализация БД
│   └── models.py       # Все операции с данными
├── handlers/
│   ├── start.py        # /start, профиль, помощь
│   ├── catalog.py      # Каталог товаров
│   ├── cart.py         # Корзина и оформление заказа
│   ├── orders.py       # История заказов
│   ├── search.py       # Поиск товаров
│   └── admin.py        # Панель администратора
└── keyboards/
    ├── reply.py        # Кнопки главного меню
    └── inline.py       # Inline-кнопки
```

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Главное меню |
| `/admin` | Панель администратора |
| `/setphone` | Изменить телефон |
| `/setaddress` | Изменить адрес |
>>>>>>> a3f6ff9e60154a5b9e6d149779d7bbcc564473b9
