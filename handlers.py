from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from db import create_db
from menu import main_menu, game_menu, admin_menu
import aiosqlite

ADMIN_ID = 6806110770


class Form(StatesGroup):
    waiting_for_user_id = State()


async def add_user_if_not_exists(user_id, username):
    async with aiosqlite.connect('casino.db') as db:
        async with db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                await db.execute('INSERT INTO users (user_id, username) VALUES (?, ?)', (user_id, username))
                await db.commit()


async def cmd_start(message: types.Message):
    await add_user_if_not_exists(message.from_user.id, message.from_user.username)
    await message.answer("Добро пожаловать в казино! Выберите действие:", reply_markup=main_menu(message.from_user.id))


async def my_profile(message: types.Message):
    async with aiosqlite.connect('casino.db') as db:
        async with db.execute('SELECT balance, is_blocked, is_withdrawal_blocked FROM users WHERE user_id = ?',
                              (message.from_user.id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                balance, is_blocked, is_withdrawal_blocked = row
                blocked_status = f"\nБлокировка игр: {'Да' if is_blocked else 'Нет'}\nБлокировка вывода: {'Да' if is_withdrawal_blocked else 'Нет'}"
                await message.answer(f"Ваш профиль:\nБаланс: {balance} монет{blocked_status}")
            else:
                await message.answer("Профиль не найден.")


async def games(message: types.Message):
    async with aiosqlite.connect('casino.db') as db:
        async with db.execute('SELECT is_blocked FROM users WHERE user_id = ?', (message.from_user.id,)) as cursor:
            row = await cursor.fetchone()
            if row and row[0] == 1:
                await message.answer("Вы заблокированы от игр.")
                return
    await message.answer("Выберите игру:", reply_markup=game_menu())


async def withdraw(message: types.Message):
    async with aiosqlite.connect('casino.db') as db:
        async with db.execute('SELECT balance, is_withdrawal_blocked FROM users WHERE user_id = ?',
                              (message.from_user.id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                balance, is_withdrawal_blocked = row
                if is_withdrawal_blocked == 1:
                    await message.answer("Ваш баланс заблокирован. Напишите в поддержку.")
                    return
                if balance == 0:
                    await message.answer("У вас 0 монет. Вы ничего не сможете вывести.")
                    return
    await message.answer("Введите сумму для вывода:")


async def statistics(message: types.Message):
    async with aiosqlite.connect('casino.db') as db:
        async with db.execute('SELECT user_id, username, balance FROM users') as cursor:
            rows = await cursor.fetchall()
            stats = "\n".join([f"ID: {row[0]}, Ник: {row[1]}, Баланс: {row[2]} монет" for row in rows])
            await message.answer(f"Статистика:\n{stats}")


async def admin_menu_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Выберите действие:", reply_markup=admin_menu())


async def block_user_games(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите ID пользователя для блокировки игр:")
    await Form.waiting_for_user_id.set()
    await state.update_data(block_type="games")
    await callback_query.answer()


async def block_user_withdrawal(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите ID пользователя для блокировки вывода:")
    await Form.waiting_for_user_id.set()
    await state.update_data(block_type="withdrawal")
    await callback_query.answer()


async def process_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)

        async with aiosqlite.connect('casino.db') as db:
            async with db.execute('SELECT user_id, is_blocked, is_withdrawal_blocked FROM users WHERE user_id = ?',
                                  (user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    await message.answer(f"Пользователь с ID {user_id} не найден.")
                    return

                state_data = await state.get_data()
                block_type = state_data.get("block_type")
                if block_type == "games" and row[1] == 1:
                    await message.answer(f"Игры для пользователя с ID {user_id} уже заблокированы.")
                    return
                elif block_type == "withdrawal" and row[2] == 1:
                    await message.answer(f"Вывод для пользователя с ID {user_id} уже заблокирован.")
                    return

        async with aiosqlite.connect('casino.db') as db:
            if block_type == "games":
                await db.execute('UPDATE users SET is_blocked = 1 WHERE user_id = ?', (user_id,))
                await db.commit()
                await message.answer(f"Игры для пользователя с ID {user_id} успешно заблокированы.")
            elif block_type == "withdrawal":
                await db.execute('UPDATE users SET is_withdrawal_blocked = 1 WHERE user_id = ?', (user_id,))
                await db.commit()
                await message.answer(f"Вывод для пользователя с ID {user_id} успешно заблокирован.")

        if message.from_user.id != ADMIN_ID:
            await message.bot.send_message(ADMIN_ID, f"Пользователь с ID {user_id} был заблокирован.")

    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID пользователя.")
    finally:
        await state.finish()


async def process_callback(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    if data == "my_profile":
        await my_profile(callback_query.message)
    elif data == "games":
        await games(callback_query.message)
    elif data == "withdraw":
        await withdraw(callback_query.message)
    elif data == "statistics":
        await statistics(callback_query.message)
    elif data == "admin_menu":
        await admin_menu_handler(callback_query)
    elif data == "block_games":
        await block_user_games(callback_query, state)
    elif data == "block_withdrawal":
        await block_user_withdrawal(callback_query, state)
    else:
        await callback_query.answer("Действие не реализовано.")


def register_handlers(dp):
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(my_profile, lambda message: message.text == "Мой профиль")
    dp.register_message_handler(games, lambda message: message.text == "Игры")
    dp.register_message_handler(withdraw, lambda message: message.text == "Вывод средств")
    dp.register_message_handler(statistics,
                                lambda message: message.text == "Статистика" and message.from_user.id == ADMIN_ID)
    dp.register_callback_query_handler(process_callback)
    dp.register_message_handler(process_user_id, state=Form.waiting_for_user_id)