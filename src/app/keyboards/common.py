from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu(is_admin: bool) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Купить доступ", callback_data="buy"))
    builder.row(InlineKeyboardButton(text="🔑 Мой ключ", callback_data="my_key"))
    if is_admin:
        builder.row(InlineKeyboardButton(text="🛠 Админ-панель", callback_data="admin"))
    return builder


def plans_menu() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="1 месяц", callback_data="plan:monthly"))
    builder.row(InlineKeyboardButton(text="1 год (скидка)", callback_data="plan:yearly"))
    builder.row(InlineKeyboardButton(text="3 месяца", callback_data="plan:onetime_3"))
    builder.row(InlineKeyboardButton(text="6 месяцев (скидка)", callback_data="plan:onetime_6"))
    return builder
