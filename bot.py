import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import start, master, manicure, pedicure, ai_helper, callback_req

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(master.router)
    dp.include_router(manicure.router)
    dp.include_router(pedicure.router)
    dp.include_router(ai_helper.router)
    dp.include_router(callback_req.router)

    logger.info("Beauty & Shine bot started (v2 - Етап 3) ✅")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
