"""Фоновий планувальник нагадувань.
Кожні 10 хв перевіряє майбутні записи й надсилає нагадування
за ~24 год та за ~2 год до візиту.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from utils.sheets import get_upcoming_bookings, mark_reminder_sent

logger = logging.getLogger(__name__)
KYIV = ZoneInfo("Europe/Kyiv")
CHECK_INTERVAL = 600  # 10 хвилин


def _parse_appt(bk: dict) -> datetime | None:
    """Дата+час запису → datetime у часовому поясі Києва."""
    try:
        y, m, d = map(int, bk["date"].split("-"))
        hh, mm = map(int, bk["time"].split(":", 1))
        return datetime(y, m, d, hh, mm, tzinfo=KYIV)
    except Exception:
        return None


async def _send_reminder(bot, bk: dict, kind: str) -> None:
    from texts import reminder_text
    from keyboards import reminder_kb
    try:
        await bot.send_message(
            int(bk["chat_id"]),
            reminder_text(bk, kind),
            reply_markup=reminder_kb(bk["id"], kind),
            parse_mode="HTML",
        )
        logger.info(f"Reminder {kind}h sent for booking {bk['id']}")
    except Exception as e:
        logger.error(f"_send_reminder error ({bk['id']}): {e}")


async def _check(bot) -> None:
    bookings = await get_upcoming_bookings()
    now = datetime.now(KYIV)

    for bk in bookings:
        if not bk.get("chat_id"):
            continue
        appt = _parse_appt(bk)
        if appt is None:
            continue

        # нагадування за 24 год (вікно: від 24год до 3год перед візитом)
        if not bk["rem24"] and (appt - timedelta(hours=24)) <= now < (appt - timedelta(hours=3)):
            await _send_reminder(bot, bk, "24")
            await mark_reminder_sent(bk["id"], "24")

        # нагадування за 2 год (вікно: від 2год перед візитом до самого візиту)
        if not bk["rem2"] and (appt - timedelta(hours=2)) <= now < appt:
            await _send_reminder(bot, bk, "2")
            await mark_reminder_sent(bk["id"], "2")


async def reminder_loop(bot) -> None:
    """Запускається фоном при старті бота."""
    await asyncio.sleep(25)  # дати боту піднятись
    logger.info("Reminder scheduler started ⏰")
    while True:
        try:
            await _check(bot)
        except Exception as e:
            logger.error(f"reminder_loop error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)
