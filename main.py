from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from utils.logger import InterceptHandler
from utils.startup import startup
from middlewares.admin import AdminCallbackMiddleware, AdminMessageMiddleware
from database.api import create_tables, import_db
from handlers import router
import logging
import asyncio


async def main():
    await create_tables()
    
    bot = Bot(token=BOT_TOKEN, parse_mode="html")
    dp = Dispatcher()
    
    dp.include_router(router)
    dp.message.outer_middleware(AdminMessageMiddleware())
    dp.callback_query.outer_middleware(AdminCallbackMiddleware())
    
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    startup()
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.ERROR)
    asyncio.run(main())

    #asyncio.run(import_db(db_path="storage.db"))