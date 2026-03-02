from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["🛍 Каталог", "🔍 Поиск"],
            ["🛒 Корзина", "📦 Мои заказы"],
            ["👤 Профиль", "ℹ️ Помощь"],
        ],
        resize_keyboard=True,
    )


def admin_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["📊 Статистика", "📦 Все заказы"],
            ["➕ Добавить товар", "➕ Добавить категорию"],
            ["📢 Рассылка", "🗑 Удалить товар"],
            ["🏠 Главное меню"],
        ],
        resize_keyboard=True,
    )


def contact_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True)


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()
