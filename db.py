import aiosqlite

async def create_db():
    async with aiosqlite.connect('casino.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                balance REAL DEFAULT 0,
                is_blocked INTEGER DEFAULT 0,
                is_withdrawal_blocked INTEGER DEFAULT 0
            )
        ''')
        await db.commit()
        print("База данных и таблица созданы или уже существуют.")

async def check_table_structure():
    async with aiosqlite.connect('casino.db') as db:
        async with db.execute('PRAGMA table_info(users);') as cursor:
            rows = await cursor.fetchall()
            print("Структура таблицы users:")
            for row in rows:
                print(row)