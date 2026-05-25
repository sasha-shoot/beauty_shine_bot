from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import ManicureFlow
from keyboards import (manicure_types_kb, nail_lengths_kb, nail_shapes_kb,
                       date_picker_kb, time_slots_kb, confirm_kb, back_to_menu_kb)
from data import MANICURE_TYPES, NAIL_LENGTHS, NAIL_SHAPES, UA_MONTHS_FULL, fmt_time, get_by_id
from utils.sheets import get_available_times, save_booking
from utils.notifications import notify_irina, send_location_card
import texts

router = Router()


@router.callback_query(F.data == "svc:manicure")
async def start_manicure(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ManicureFlow.choosing_type)
    await callback.message.edit_text(texts.MANICURE_TYPE, reply_markup=manicure_types_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_type, F.data.startswith("mtype:"))
async def pick_type(callback: CallbackQuery, state: FSMContext):
    t = get_by_id(MANICURE_TYPES, callback.data.split(":")[1])
    await state.update_data(mtype_id=t["id"], mtype_name=t["name"],
                            base_price=t["price"], base_duration=t["duration"])
    await state.set_state(ManicureFlow.choosing_length)
    await callback.message.edit_text(texts.NAIL_LENGTH, reply_markup=nail_lengths_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_length, F.data.startswith("mlen:"))
async def pick_length(callback: CallbackQuery, state: FSMContext):
    l = get_by_id(NAIL_LENGTHS, callback.data.split(":")[1])
    await state.update_data(mlen_name=l["name"], len_price=l["price_add"], len_time=l["time_add"])
    await state.set_state(ManicureFlow.choosing_shape)
    await callback.message.edit_text(texts.NAIL_SHAPE, reply_markup=nail_shapes_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_shape, F.data.startswith("mshape:"))
async def pick_shape(callback: CallbackQuery, state: FSMContext):
    s = get_by_id(NAIL_SHAPES, callback.data.split(":")[1])
    await state.update_data(mshape_name=s["name"], shape_price=s["price_add"], shape_time=s["time_add"])

    data = await state.get_data()
    total_price    = data["base_price"]    + data["len_price"]  + data["shape_price"]
    total_duration = data["base_duration"] + data["len_time"]   + data["shape_time"]
    await state.update_data(total_price=total_price, total_duration=total_duration)

    await state.set_state(ManicureFlow.choosing_date)
    text = texts.manicure_summary(
        data["mtype_name"], data["mlen_name"], s["name"],
        fmt_time(total_duration), total_price, ""
    )
    await callback.message.edit_text(text, reply_markup=date_picker_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_date, F.data.startswith("date:"))
async def pick_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":")[1]
    await state.update_data(date=date_str)

    from datetime import date
    d = date.fromisoformat(date_str)
    date_ua = f"{d.day} {UA_MONTHS_FULL[d.month]}"
    await state.update_data(date_ua=date_ua)

    data = await state.get_data()
    available = await get_available_times(date_str, "Манікюр")

    await state.set_state(ManicureFlow.choosing_time)
    if not available:
        await callback.message.edit_text(texts.NO_SLOTS, reply_markup=date_picker_kb(), parse_mode="HTML")
    else:
        text = texts.time_choice_text(date_ua, fmt_time(data["total_duration"]))
        await callback.message.edit_text(text, reply_markup=time_slots_kb(available), parse_mode="HTML")
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_time, F.data.startswith("time:"))
async def pick_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split(":", 1)[1]
    data = await state.get_data()

    # перевірка знижки на цей слот
    from utils.sheets import get_discount_for_slot
    discount = await get_discount_for_slot(data["date"], time_str, "Манікюр")
    base_price = data["total_price"]
    if discount > 0:
        final_price = round(base_price * (100 - discount) / 100)
    else:
        final_price = base_price

    await state.update_data(time=time_str, discount=discount, final_price=final_price)

    service_detail = f"{data['mtype_name']} · {data['mlen_name']} · {data['mshape_name']}"
    text = texts.manicure_confirm_text(
        data["mtype_name"], data["mlen_name"], data["mshape_name"],
        data["date_ua"], time_str, fmt_time(data["total_duration"]), base_price
    )
    if discount > 0:
        text += (f"\n\n🎁 <b>Знижка −{discount}%</b>"
                 f"\n💰 До сплати: <b>{final_price} грн</b>")
    await state.update_data(service_detail=service_detail)
    await state.set_state(ManicureFlow.confirming)
    await callback.message.edit_text(text, reply_markup=confirm_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_time, F.data == "back:date")
async def back_to_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ManicureFlow.choosing_date)
    data = await state.get_data()
    text = texts.manicure_summary(
        data["mtype_name"], data["mlen_name"], data["mshape_name"],
        fmt_time(data["total_duration"]), data["total_price"], ""
    )
    await callback.message.edit_text(text, reply_markup=date_picker_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(ManicureFlow.confirming, F.data == "confirm:yes")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user
    discount = data.get("discount", 0)
    final_price = data.get("final_price", data["total_price"])

    note = f"Знижка −{discount}%" if discount > 0 else ""
    await save_booking(
        date=data["date"], time=data["time"],
        client_name=user.full_name, client_username=user.username or "",
        service="Манікюр", details=data["service_detail"],
        price=final_price, duration=data["total_duration"], notes=note,
        chat_id=user.id,
    )

    await notify_irina(
        bot=callback.bot,
        client_name=user.full_name, client_username=user.username,
        service_detail=data["service_detail"],
        date=data["date_ua"], time=data["time"],
        price=final_price, duration=fmt_time(data["total_duration"]),
        discount=discount,
    )

    await state.clear()
    await callback.message.edit_text(
        texts.booking_confirmed(data["date_ua"], data["time"],
                                data["service_detail"], final_price),
        reply_markup=back_to_menu_kb(), parse_mode="HTML"
    )
    await send_location_card(callback.bot, callback.from_user.id)
    await callback.answer()


@router.callback_query(ManicureFlow.confirming, F.data == "confirm:no")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    from keyboards import main_menu_kb
    await callback.message.edit_text(texts.WELCOME, reply_markup=main_menu_kb(), parse_mode="HTML")
    await callback.answer("Запис скасовано")
