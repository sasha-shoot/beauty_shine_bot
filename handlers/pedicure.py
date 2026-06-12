"""Педикюр-флоу. Вхід — у start.py (фото Івана + опис + кнопки).
Кроки тут: дата → час → підтвердження. _edit() підтримує і фото (edit_caption), і текст."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import PedicureFlow
from keyboards import date_picker_kb, time_slots_kb, confirm_kb, back_to_menu_kb
from data import UA_MONTHS_FULL
from utils.sheets import get_available_times, save_booking, get_discount_for_slot
from utils.notifications import notify_ivan_booking, notify_ivan_callback, send_location_card
import texts

router = Router()


async def _edit(msg, text, kb=None):
    if msg.photo:
        await msg.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
    else:
        await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(PedicureFlow.choosing_action, F.data == "ped:date")
async def ped_choose_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PedicureFlow.choosing_date)
    await _edit(callback.message, texts.CHOOSE_DATE, date_picker_kb())
    await callback.answer()


@router.callback_query(PedicureFlow.choosing_action, F.data == "ped:call")
async def ped_call(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = callback.from_user
    await notify_ivan_callback(
        bot=callback.bot,
        client_name=user.full_name, client_username=user.username,
        phone="(не вказано)", question="Консультація перед педикюром",
    )
    await _edit(callback.message, texts.CALLBACK_CONFIRMED, back_to_menu_kb())
    await callback.answer()


@router.callback_query(PedicureFlow.choosing_date, F.data.startswith("date:"))
async def ped_pick_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":")[1]
    await state.update_data(date=date_str)
    from datetime import date
    d = date.fromisoformat(date_str)
    date_ua = f"{d.day} {UA_MONTHS_FULL[d.month]}"
    await state.update_data(date_ua=date_ua)

    available = await get_available_times(date_str, "Педикюр")
    if not available:
        await state.set_state(PedicureFlow.choosing_date)
        await _edit(callback.message, texts.NO_SLOTS, date_picker_kb())
    else:
        await state.set_state(PedicureFlow.choosing_time)
        await _edit(
            callback.message,
            f"📅 <b>{date_ua}</b>\n\nОберіть зручний час:",
            time_slots_kb(available),
        )
    await callback.answer()


@router.callback_query(PedicureFlow.choosing_time, F.data.startswith("time:"))
async def ped_pick_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split(":", 1)[1]
    data = await state.get_data()
    discount = await get_discount_for_slot(data["date"], time_str, "Педикюр")
    await state.update_data(time=time_str, discount=discount)

    text = texts.pedicure_confirm_text(data["date_ua"], time_str, discount=discount)
    await state.set_state(PedicureFlow.confirming)
    await _edit(callback.message, text, confirm_kb())
    await callback.answer()


@router.callback_query(PedicureFlow.choosing_time, F.data == "back:date")
async def ped_back_to_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PedicureFlow.choosing_date)
    await _edit(callback.message, texts.CHOOSE_DATE, date_picker_kb())
    await callback.answer()


@router.callback_query(PedicureFlow.confirming, F.data == "confirm:yes")
async def ped_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user
    discount = data.get("discount", 0)
    note = f"Знижка −{discount}%" if discount > 0 else ""

    await save_booking(
        date=data["date"], time=data["time"],
        client_name=user.full_name, client_username=user.username or "",
        service="Педикюр", details="Педикюр",
        price="", duration="", notes=note,
        chat_id=user.id,
    )
    await notify_ivan_booking(
        bot=callback.bot,
        client_name=user.full_name, client_username=user.username,
        date=data["date_ua"], time=data["time"], discount=discount,
    )

    await state.clear()
    # Вікно стає ТЕРМІНАЛЬНОЮ карткою запису (без кнопок, лишається в історії)
    await _edit(
        callback.message,
        texts.pedicure_confirmed(data["date_ua"], data["time"], discount=discount),
        None,
    )
    from utils import ui_state
    ui_state.forget_window(callback.message.chat.id)
    await send_location_card(callback.bot, callback.from_user.id)
    from handlers.start import show_menu_new_window
    await show_menu_new_window(callback.bot, callback.message.chat.id, callback.from_user.id, state)
    await callback.answer("✅ Запис підтверджено!")


@router.callback_query(PedicureFlow.confirming, F.data == "confirm:no")
async def ped_cancel(callback: CallbackQuery, state: FSMContext):
    from handlers.start import show_menu_in_window
    await show_menu_in_window(callback, state)
    await callback.answer("Скасовано")
