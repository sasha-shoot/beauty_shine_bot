"""Манікюр-флоу. Вхід — у start.py (фото Ірини + опис + типи).
Цей файл містить кроки після вибору типу: довжина → форма → дата → час → підтвердження.
Усі повідомлення редагуються через _edit() — підтримує і фото (edit_caption), і текст."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from states import ManicureFlow
from keyboards import (
    nail_lengths_kb, nail_shapes_kb,
    date_picker_kb, time_slots_kb, confirm_kb, back_to_menu_kb,
)
from data import MANICURE_TYPES, NAIL_LENGTHS, NAIL_SHAPES, UA_MONTHS_FULL, get_by_id
from utils.sheets import (get_available_times, save_booking, get_discount_for_slot,
                          get_duration_map, calc_manicure_duration)
from utils.notifications import notify_irina, send_location_card
import texts

router = Router()


async def _edit(msg, text, kb=None):
    """Універсальне редагування: edit_caption для фото-повідомлень, edit_text для текстових."""
    if msg.photo:
        await msg.edit_caption(caption=text, reply_markup=kb, parse_mode="HTML")
    else:
        await msg.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(ManicureFlow.choosing_type, F.data.startswith("mtype:"))
async def pick_type(callback: CallbackQuery, state: FSMContext):
    t = get_by_id(MANICURE_TYPES, callback.data.split(":")[1])
    if not t:
        await callback.answer()
        return
    await state.update_data(mtype_name=t["name"])
    await state.set_state(ManicureFlow.choosing_length)
    await _edit(callback.message, texts.NAIL_LENGTH, nail_lengths_kb())
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_length, F.data.startswith("mlen:"))
async def pick_length(callback: CallbackQuery, state: FSMContext):
    l = get_by_id(NAIL_LENGTHS, callback.data.split(":")[1])
    if not l:
        await callback.answer()
        return
    await state.update_data(mlen_name=l["name"])
    await state.set_state(ManicureFlow.choosing_shape)
    await _edit(callback.message, texts.NAIL_SHAPE, nail_shapes_kb())
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_shape, F.data.startswith("mshape:"))
async def pick_shape(callback: CallbackQuery, state: FSMContext):
    s = get_by_id(NAIL_SHAPES, callback.data.split(":")[1])
    if not s:
        await callback.answer()
        return
    await state.update_data(mshape_name=s["name"])
    await state.set_state(ManicureFlow.choosing_date)
    data = await state.get_data()
    summary = texts.manicure_chosen_text(
        data["mtype_name"], data["mlen_name"], s["name"]
    )
    await _edit(callback.message, summary, date_picker_kb())
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_date, F.data.startswith("date:"))
async def pick_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":")[1]
    await state.update_data(date=date_str)

    from datetime import date
    d = date.fromisoformat(date_str)
    date_ua = f"{d.day} {UA_MONTHS_FULL[d.month]}"
    await state.update_data(date_ua=date_ua)

    # Тривалість обраної процедури визначає, які слоти реально вільні
    data_state = await state.get_data()
    durations = await get_duration_map()
    duration = calc_manicure_duration(
        durations,
        data_state.get("mtype_name", ""),
        data_state.get("mlen_name", ""),
    )
    await state.update_data(duration=duration)

    available = await get_available_times(date_str, "Манікюр", duration_min=duration)
    await state.set_state(ManicureFlow.choosing_time)
    if not available:
        await _edit(callback.message, texts.NO_SLOTS, date_picker_kb())
    else:
        text = f"📅 <b>{date_ua}</b>\n\n{texts.CHOOSE_TIME}"
        await _edit(callback.message, text, time_slots_kb(available))
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_time, F.data.startswith("time:"))
async def pick_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split(":", 1)[1]
    data = await state.get_data()

    discount = await get_discount_for_slot(data["date"], time_str, "Манікюр")
    service_detail = f"{data['mtype_name']} · {data['mlen_name']} · {data['mshape_name']}"
    # Жива ціна з таблиці «Ціни» (кеш 60 сек)
    from utils.sheets import get_price_list, calc_manicure_price
    prices = await get_price_list()
    price = calc_manicure_price(prices, data["mtype_name"], data["mlen_name"])

    await state.update_data(time=time_str, discount=discount,
                            service_detail=service_detail, price=price)

    text = texts.manicure_confirm_text(
        data["mtype_name"], data["mlen_name"], data["mshape_name"],
        data["date_ua"], time_str, discount=discount, price=price,
    )
    await state.set_state(ManicureFlow.confirming)
    await _edit(callback.message, text, confirm_kb())
    await callback.answer()


@router.callback_query(ManicureFlow.choosing_time, F.data == "back:date")
async def back_to_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ManicureFlow.choosing_date)
    data = await state.get_data()
    summary = texts.manicure_chosen_text(
        data["mtype_name"], data["mlen_name"], data["mshape_name"]
    )
    await _edit(callback.message, summary, date_picker_kb())
    await callback.answer()


@router.callback_query(ManicureFlow.confirming, F.data == "confirm:yes")
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = callback.from_user
    discount = data.get("discount", 0)
    note = f"Знижка −{discount}%" if discount > 0 else ""

    await save_booking(
        date=data["date"], time=data["time"],
        client_name=user.full_name, client_username=user.username or "",
        service="Манікюр", details=data["service_detail"],
        price=(str(round(data.get("price", 0) * (100 - discount) / 100))
               if data.get("price") else ""),
        duration=(str(data.get("duration")) if data.get("duration") else ""),
        notes=note,
        chat_id=user.id,
    )

    await notify_irina(
        bot=callback.bot,
        client_name=user.full_name, client_username=user.username,
        service_detail=data["service_detail"],
        date=data["date_ua"], time=data["time"],
        discount=discount,
    )

    await state.clear()
    # Вікно стає ТЕРМІНАЛЬНОЮ карткою запису (без кнопок, лишається в історії)
    await _edit(
        callback.message,
        texts.booking_confirmed(data["date_ua"], data["time"],
                                data["service_detail"], discount=discount,
                                price=data.get("price", 0)),
        None,
    )
    from utils import ui_state
    ui_state.forget_window(callback.message.chat.id)  # картку не видаляємо новим вікном
    await send_location_card(callback.bot, callback.from_user.id)
    # Нове вікно з головним меню — знизу
    from handlers.start import show_menu_new_window
    await show_menu_new_window(callback.bot, callback.message.chat.id, callback.from_user.id, state)
    await callback.answer("✅ Запис підтверджено!")


@router.callback_query(ManicureFlow.confirming, F.data == "confirm:no")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    # редагуємо вікно назад у головне меню — без нових повідомлень
    from handlers.start import show_menu_in_window
    await show_menu_in_window(callback, state)
    await callback.answer("Скасовано")
