from aiogram import types

ADMIN_ID = АЙДИ АДМИНА. ПРОСТО ВСТАВЬ ЦИФРЫ

def main_menu(user_id):
    keyboard = types.InlineKeyboardMarkup()
    if user_id == ADMIN_ID:
        keyboard.add(
            types.InlineKeyboardButton("Мой профиль", callback_data="my_profile"),
            types.InlineKeyboardButton("Статистика", callback_data="statistics"),
            types.InlineKeyboardButton("Выплаты", callback_data="payouts"),
            types.InlineKeyboardButton("Настройка казино", callback_data="casino_settings"),
            types.InlineKeyboardButton("Админ меню", callback_data="admin_menu")
        )
    else:
        keyboard.add(
            types.InlineKeyboardButton("Мой профиль", callback_data="my_profile"),
            types.InlineKeyboardButton("Игры", callback_data="games"),
            types.InlineKeyboardButton("Вывод средств", callback_data="withdraw")
        )
    return keyboard

def admin_menu():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("Блокировка игр", callback_data="block_games"),
        types.InlineKeyboardButton("Блокировка вывода", callback_data="block_withdrawal")
    )
    return keyboard

def game_menu():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("Ставки на числа", callback_data="bet_on_numbers"),
        types.InlineKeyboardButton("Кости", callback_data="dice"),
        types.InlineKeyboardButton("Слот-машина", callback_data="slot_machine")
    )
    return keyboard
