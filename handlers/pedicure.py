from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import PedicureFlow
from keyboards import pedicure_options_kb, date_picker_kb, time_slots_kb, confirm_kb, back_to_menu_kb
from data import UA_MONTHS_FULL, fmt_time
from utils.sheets import get_available_times, save_booking
from utils.notifications import notify_ivan_booking, notify_ivan_callback, send_location_card
import texts

router = Router()


@router.callback_query(F.data == "svc:pedicure")
async def start_pedicure(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PedicureFlow.choosing_action)
    await callback.message.edit_text(texts.PEDICURE_INTRO, reply_markup=pedicure_options_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(PedicureFlow.choosing_action, F.data == "ped:date")
async def ped_choose_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PedicureFlow.choosing_date)
    await callback.message.edit_text(texts.CHOOSE_DATE, reply_markup=date_picker_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(PedicureFlow.choosing_action, F.data == "ped:call")
async def ped_call(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = callback.from_user
    await notify_ivan_callback(
        bot=callback.bot,
        client_name=user.full_name, client_username=user.username,
        phone="(не вказано)", question="Консультація перед педикюром"
    )
    await callback.message.edit_text(texts.CALLBACK_CONFIRMED, reply_markup=back_to_menu_kb(), parse_mode="HTML")
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
    await state.set_state(PedicureFlow.choosing_time)

    if not available:
        await state.set_state(PedicureFlow.choosing_date)
        await callback.message.edit_text(texts.NO_SLOTS, reply_markup=date_picker_kb(), parse_mode="HTML")
    else:
        await callback.message.edit_text(
            f"📅 <b>{date_ua}</b>\n\nОберіть зручний час:",
            reply_markup=time_slots_kb(available), parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(PedicureFlow.choosing_time, F.data.startswith("time:"))
async def ped_pick_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split(":", 1)[1]
    data = await state.get_data()

    from utils.sheets import get_discount_for_slot
    discount = await get_discount_for_slot(data["date"], time_str, "Педикюр")
    await state.update_data(time=time_str, discount=discount)

    text = texts.pedicure_confirm_text(data["date_ua"], time_str)
    if discount > 0:
        text += f"\n\n🎁 <b>Знижка −{discount}%</b> — майстер врахує при розрахунку"
    await state.set_state(PedicureFlow.confirming)
    await callback.message.edit_text(text, reply_markup=confirm_kb(), parse_mode="HTML")
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
        service="Педикюр", details="Педикюр медичний + косметичний",
        price="уточнюється", duration="1-2 год", notes=note,
    )
    await notify_ivan_booking(
        bot=callback.bot,
        client_name=user.full_name, client_username=user.username,
        date=data["date_ua"], time=data["time"], discount=discount,
    )

    await state.clear()
    await callback.message.edit_text(
        texts.pedicure_confirmed(data["date_ua"], data["time"]),
        reply_markup=back_to_menu_kb(), parse_mode="HTML"
    )
    await send_location_card(callback.bot, callback.from_user.id)
    await callback.answer()


@router.callback_query(PedicureFlow.confirming, F.data == "confirm:no")
async def ped_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    from keyboards import main_menu_kb
    await callback.message.edit_text(texts.WELCOME, reply_markup=main_menu_kb(), parse_mode="HTML")
    await callback.answer("Запис скасовано")
