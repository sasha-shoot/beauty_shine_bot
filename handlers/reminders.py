from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import reschedule_confirm_kb
from utils.sheets import get_booking_by_id
from utils.notifications import notify_master_reschedule
import texts

router = Router()


@router.callback_query(F.data == "remok")
async def reminder_ok(callback: CallbackQuery):
    await callback.message.edit_text(texts.REMINDER_OK, parse_mode="HTML")
    await callback.answer("Дякуємо!")


@router.callback_query(F.data.startswith("remmv:"))
async def reminder_move(callback: CallbackQuery):
    parts = callback.data.split(":")
    rec_id, kind = parts[1], parts[2]

    booking = await get_booking_by_id(rec_id)
    if not booking:
        await callback.message.edit_text(texts.RESCHEDULE_NOT_FOUND, parse_mode="HTML")
        await callback.answer()
        return

    if kind == "24":
        # м'яке перенесення — без штрафу
        await notify_master_reschedule(callback.bot, booking, penalty=False)
        await callback.message.edit_text(texts.RESCHEDULE_SOFT, parse_mode="HTML")
    else:
        # перенесення за <2 год — попередження про штраф
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
    await callback.answer()


@router.callback_query(F.data == "rempencancel")
async def reminder_penalty_cancel(callback: CallbackQuery):
    await callback.message.edit_text(texts.RESCHEDULE_CANCELLED, parse_mode="HTML")
    await callback.answer()
