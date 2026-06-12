"""Реєстр «вікон» — єдиного UI-повідомлення на чат.

Вікно — це фото-повідомлення з caption та inline-кнопками, яке бот
редагує при навігації замість надсилання нових повідомлень.

Зберігається в пам'яті процесу. Після рестарту бота реєстр порожній —
це ОК: перший же /start чи «🏠 Меню» створить нове вікно, а старе
повідомлення просто залишиться в історії без наслідків.
"""
import logging

logger = logging.getLogger(__name__)

# chat_id -> message_id вікна
_windows: dict[int, int] = {}


def set_window(chat_id: int, message_id: int) -> None:
    _windows[chat_id] = message_id


def get_window(chat_id: int) -> int | None:
    return _windows.get(chat_id)


def forget_window(chat_id: int) -> None:
    _windows.pop(chat_id, None)


async def delete_window(bot, chat_id: int) -> None:
    """Видаляє старе вікно з чату (якщо знаємо про нього). Безпечно ковтає помилки
    (повідомлення могло бути видалене вручну або бути старшим за 48 год)."""
    mid = _windows.pop(chat_id, None)
    if mid is None:
        return
    try:
        await bot.delete_message(chat_id=chat_id, message_id=mid)
    except Exception as e:
        logger.debug(f"delete_window: не вдалося видалити {mid} у {chat_id}: {e}")
