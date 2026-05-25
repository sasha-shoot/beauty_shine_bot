import asyncio
from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import reschedule_confirm_kb
from utils.sheets import get_booking_by_id
from utils.notifications import notify_master_reschedule
import texts

router = Router()


async def _delete_after(bot, chat_id: int, message_id: int, delay: int = 600) -> None:
    """Видаляє повідомлення через delay секунд (за замовчуванням — 10 хв)."""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id, message_id)
    except Exception:
        pass


@router.callback_query(F.data == "remok")
async def reminder_ok(callback: CallbackQuery):
    """Клієнт підтвердив візит — прибираємо нагадування з чату."""
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Дякуємо! Чекаємо на вас 💜")


@router.callback_query(F.data.startswith("remmv:"))
async def reminder_move(callback: CallbackQuery):
    parts = callback.data.split(":")
    rec_id, kind = parts[1], parts[2]

    booking = await get_booking_by_id(rec_id)
    if not booking:
        await callback.message.edit_text(texts.RESCHEDULE_NOT_FOUND, parse_mode="HTML")
        asyncio.create_task(_delete_after(
            callback.bot, callback.message.chat.id, callback.message.message_id))
        await callback.answer()
        return

    if kind == "24":
        # м'яке перенесення — без штрафу
        await notify_master_reschedule(callback.bot, booking, penalty=False)
        await callback.message.edit_text(texts.RESCHEDULE_SOFT, parse_mode="HTML")
        # повідомлення про дзвінок майстра зникне через 10 хв
        asyncio.create_task(_delete_after(
            callback.bot, callback.message.chat.id, callback.message.message_id))
    else:
        # перенесення за <2 год — попередження про штраф (лишається до рішення)
        await callback.message.edit_text(
            texts.reschedule_penalty_warn(booking),
            reply_markup=reschedule_confirm_kb(rec_id),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data.startswith("rempen:"))
async def reminder_penalty_confirm(callback: CallbackQuery):
    rec_id = callback.data.split(":", 1)[1]
    booking = await get_booking_by_id(rec_id)
    if booking:
        await notify_master_reschedule(callback.bot, booking, penalty=True)
    await callback.message.edit_text(texts.RESCHEDULE_PENALTY_DONE, parse_mode="HTML")
    asyncio.create_task(_delete_after(
        callback.bot, callback.message.chat.id, callback.message.message_id))
    await callback.answer()


@router.callback_query(F.data == "rempencancel")
async def reminder_penalty_cancel(callback: CallbackQuery):
    """Клієнт передумав переносити — лишає запис, прибираємо нагадування."""
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer("Добре, чекаємо на вас 💜")
