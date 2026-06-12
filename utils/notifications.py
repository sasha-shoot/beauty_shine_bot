import logging
from aiogram import Bot
from config import IRINA_CHAT_ID, IVAN_CHAT_ID

logger = logging.getLogger(__name__)


def _tg_link(name: str, username: str | None) -> str:
    if username:
        return f'<a href="tg://user?id=0">@{username}</a> ({name})'
    return name


async def notify_irina(
    bot: Bot,
    client_name: str,
    client_username: str | None,
    service_detail: str,
    date: str,
    time: str,
    discount: int = 0,
) -> None:
    """Новий запис на манікюр → Ірина."""
    disc_line = f"\n🎁 Знижка: −{discount}% — врахувати при розрахунку" if discount > 0 else ""
    text = (
        f"💅 <b>Новий запис на манікюр</b>\n\n"
        f"👤 Клієнт: {_tg_link(client_name, client_username)}\n"
        f"📋 Послуга: {service_detail}\n"
        f"📅 Дата: {date} о {time}{disc_line}"
    )
    try:
        await bot.send_message(IRINA_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"notify_irina error: {e}")


async def notify_ivan_booking(
    bot: Bot,
    client_name: str,
    client_username: str | None,
    date: str,
    time: str,
    discount: int = 0,
) -> None:
    """Новий запис на педикюр → Іван."""
    disc_line = f"\n🎁 Знижка: −{discount}% — врахувати при розрахунку" if discount > 0 else ""
    text = (
        f"🦶 <b>Новий запис на педикюр</b>\n\n"
        f"👤 Клієнт: {_tg_link(client_name, client_username)}\n"
        f"📅 Дата: {date} о {time}\n"
        f"⏱ Тривалість: узгоджується індивідуально{disc_line}"
    )
    try:
        await bot.send_message(IVAN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"notify_ivan_booking error: {e}")


async def notify_ivan_callback(
    bot: Bot,
    client_name: str,
    client_username: str | None,
    phone: str,
    question: str,
    ai_flag: bool = False,
) -> None:
    """Заявка на дзвінок → Іван."""
    flag = "⚠️ <b>Зверніть увагу: ШІ-помічник виявив симптоми</b>\n\n" if ai_flag else ""
    text = (
        f"📞 <b>Заявка на дзвінок</b>\n\n"
        f"{flag}"
        f"👤 Клієнт: {_tg_link(client_name, client_username)}\n"
        f"📱 Телефон: {phone}\n"
        f"💬 Питання: {question or '—'}"
    )
    try:
        await bot.send_message(IVAN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"notify_ivan_callback error: {e}")


async def notify_ivan_ai_alert(
    bot: Bot,
    client_name: str,
    client_username: str | None,
    symptom: str,
    ai_summary: str,
) -> None:
    """ШІ виявив медичну проблему → Іван."""
    text = (
        f"🚨 <b>ШІ-помічник: зверніть увагу</b>\n\n"
        f"👤 Клієнт: {_tg_link(client_name, client_username)}\n\n"
        f"💬 <b>Скарга:</b> {symptom}\n\n"
        f"🤖 <b>Аналіз ШІ:</b> {ai_summary}"
    )
    try:
        await bot.send_message(IVAN_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"notify_ivan_ai_alert error: {e}")


# ── Гео-картка салону ─────────────────────────────────────
# Коротке посилання Google Maps салону (з прев'ю в Telegram)
SALON_MAPS_LINK = "https://maps.app.goo.gl/UqfNiH2MrMT5xkuv8"


async def send_location_card(bot: Bot, chat_id: int) -> None:
    """Надсилає клієнту картку локації після підтвердження запису:
    одне текстове повідомлення з посиланням на Google Maps (з прев'ю)."""
    from config import SALON_ADDRESS, SALON_PHONE
    import texts
    try:
        await bot.send_message(
            chat_id,
            texts.geo_card(SALON_ADDRESS, SALON_PHONE, SALON_MAPS_LINK),
            parse_mode="HTML",
            disable_web_page_preview=False,  # прев'ю карти увімкнене
        )
    except Exception as e:
        logger.error(f"send_location_card error: {e}")


# ── Сповіщення майстру про перенесення ───────────────────
async def notify_master_reschedule(bot: Bot, booking: dict, penalty: bool) -> None:
    """Повідомляє майстра що клієнт переносить запис."""
    from config import IRINA_CHAT_ID, IVAN_CHAT_ID
    service = booking.get("service", "")
    if service == "Манікюр":
        chat_id, icon = IRINA_CHAT_ID, "💅"
    else:
        chat_id, icon = IVAN_CHAT_ID, "🦶"

    pen_line = ""
    if penalty:
        pen_line = ("\n\n⚠️ <b>Пізнє перенесення (&lt;2 год).</b>\n"
                    "Застосувати +50% до наступного візиту.")

    text = (
        f"🔄 <b>Клієнт переносить запис</b>\n\n"
        f"{icon} {service}\n"
        f"👤 {booking.get('name', '—')} {booking.get('username', '')}\n"
        f"📅 Було записано: {booking.get('date')} о {booking.get('time')}"
        f"{pen_line}\n\n"
        f"📞 Зателефонуйте клієнту, щоб підібрати нову дату."
    )
    try:
        await bot.send_message(chat_id, text, parse_mode="HTML")
    except Exception as e:
        logger.error(f"notify_master_reschedule error: {e}")
