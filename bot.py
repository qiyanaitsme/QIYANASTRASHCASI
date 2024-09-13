import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import register_handlers
from db import create_db, check_table_structure

API_TOKEN = 'ТОКЕН БОТА'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def on_startup(dp):
    try:
        await create_db()
        await check_table_structure()
    except Exception as e:
        logging.error(f"Ошибка при создании базы данных: {e}")

if __name__ == '__main__':
    register_handlers(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)