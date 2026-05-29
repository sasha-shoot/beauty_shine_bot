"""Beauty & Shine — головний файл бота.
Порядок реєстрації роутерів критичний:
1. start  — глобальні кнопки нижнього меню + команди (escape-hatch з будь-якого стану)
2. master — авторизація та панель майстра
3. reminders — кнопки нагадувань
4. далі — флоу (манікюр, педикюр, ШІ, дзвінок)
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from config import BOT_TOKEN
from handlers import (
    start, master, manicure, pedicure,
    ai_helper, callback_req, reminders,
)
from utils.scheduler import reminder_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


COMMANDS = [
    BotCommand(command="start",   description="Головне меню"),
    BotCommand(command="zapys",   description="Записатись на послугу"),
    BotCommand(command="ai",      description="ШІ помічник"),
    BotCommand(command="skidky",  description="Слоти зі знижкою"),
    BotCommand(command="help",    description="Про бота / довідка"),
]


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # 1) start — головні кнопки нижнього меню + команди (реєструється першим!)
    dp.include_router(start.router)
    # 2) master — авторизація та власні кнопки
    dp.include_router(master.router)
    # 3) reminders — callbacks нагадувань
    dp.include_router(reminders.router)
    # 4) флоу
    dp.include_router(manicure.router)
    dp.include_router(pedicure.router)
    dp.include_router(ai_helper.router)
    dp.include_router(callback_req.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(COMMANDS)
    logger.info("Beauty & Shine bot started (v3 — Westelecom-style menu) ✅")

    # Фоновий планувальник нагадувань
    asyncio.create_task(reminder_loop(bot))

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
