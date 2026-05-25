from datetime import date
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import MasterAuth, MasterFlow
from keyboards import (master_menu_kb, master_service_kb, master_date_kb,
                       slot_grid_kb, back_to_master_kb)
from config import MASTER_PASSWORD
from data import TIME_SLOTS, UA_MONTHS_FULL
from utils.settings import is_maintenance, set_maintenance
from utils.sheets import (get_bookings_for_date, get_blocked_for_service,
                          get_booked_times, save_blocked_slots)
import texts

router = Router()


def _date_ua(date_str: str) -> str:
    d = date.fromisoformat(date_str)
    return f"{d.day} {UA_MONTHS_FULL[d.month]}"


# ══ АВТОРИЗАЦІЯ ══════════════════════════════════════════
@router.callback_query(F.data == "role:master")
async def role_master(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MasterAuth.entering_password)
    await callback.message.edit_text(texts.MASTER_PASSWORD_PROMPT, parse_mode="HTML")
    await callback.answer()


@router.message(MasterAuth.entering_password)
async def check_password(message: Message, state: FSMContext):
    if (message.text or "").strip() == MASTER_PASSWORD:
        await state.clear()
        await message.answer(
            texts.master_menu_text(is_maintenance()),
            reply_markup=master_menu_kb(is_maintenance()),
            parse_mode="HTML",
        )
    else:
        await message.answer(texts.MASTER_WRONG_PASSWORD, parse_mode="HTML")


# ══ ПАНЕЛЬ МАЙСТРА ═══════════════════════════════════════
@router.callback_query(F.data == "master:menu")
async def master_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        texts.master_menu_text(is_maintenance()),
        reply_markup=master_menu_kb(is_maintenance()),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "master:maintenance")
async def toggle_maintenance(callback: CallbackQuery):
    new_value = not is_maintenance()
    set_maintenance(new_value)
    await callback.message.edit_text(
        texts.master_menu_text(new_value),
        reply_markup=master_menu_kb(new_value),
        parse_mode="HTML",
    )
    await callback.answer("Тех. режим " + ("увімкнено" if new_value else "вимкнено"))


# ══ ІСТОРІЯ ЗА ДЕНЬ ══════════════════════════════════════
@router.callback_query(F.data == "master:history")
async def history_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MasterFlow.hist_date)
    await callback.message.edit_text(
        texts.MASTER_HISTORY_PICK,
        reply_markup=master_date_kb("histdate"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(MasterFlow.hist_date, F.data.startswith("histdate:"))
async def history_show(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":", 1)[1]
    bookings = await get_bookings_for_date(date_str)
    await state.clear()
    await callback.message.edit_text(
        texts.master_history(_date_ua(date_str), bookings),
        reply_markup=back_to_master_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


# ══ МЕНЕДЖМЕНТ ВІКОН ═════════════════════════════════════
@router.callback_query(F.data == "master:windows")
async def wm_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MasterFlow.wm_service)
    await callback.message.edit_text(
        texts.MASTER_WM_SERVICE,
        reply_markup=master_service_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(MasterFlow.wm_service, F.data.startswith("wmsvc:"))
async def wm_pick_service(callback: CallbackQuery, state: FSMContext):
    svc = callback.data.split(":", 1)[1]
    service_name = "Манікюр" if svc == "manicure" else "Педикюр"
    await state.update_data(wm_service=service_name)
    await state.set_state(MasterFlow.wm_date)
    await callback.message.edit_text(
        texts.master_wm_date(service_name),
        reply_markup=master_date_kb("wmdate"),
        parse_mode="HTML",
    )
    await callback.answer()


async def _render_grid(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    blocked = set(data.get("wm_blocked", []))
    booked  = set(data.get("wm_booked", []))
    text = texts.master_wm_grid(data["wm_service"], _date_ua(data["wm_date"]))
    await callback.message.edit_text(
        text, reply_markup=slot_grid_kb(blocked, booked), parse_mode="HTML"
    )


@router.callback_query(MasterFlow.wm_date, F.data.startswith("wmdate:"))
async def wm_pick_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":", 1)[1]
    data = await state.get_data()
    service = data["wm_service"]

    blocked_map = await get_blocked_for_service(date_str, service)
    booked = await get_booked_times(date_str, service)

    await state.update_data(
        wm_date=date_str,
        wm_blocked=list(blocked_map.keys()),
        wm_original=blocked_map,
        wm_booked=list(booked),
    )
    await state.set_state(MasterFlow.wm_editing)
    await _render_grid(callback, state)
    await callback.answer()


@router.callback_query(MasterFlow.wm_editing, F.data.startswith("wmslot:"))
async def wm_toggle_slot(callback: CallbackQuery, state: FSMContext):
    slot = callback.data.split(":", 1)[1]
    data = await state.get_data()
    blocked = set(data.get("wm_blocked", []))
    if slot in blocked:
        blocked.discard(slot)
    else:
        blocked.add(slot)
    await state.update_data(wm_blocked=list(blocked))
    await _render_grid(callback, state)
    await callback.answer()


@router.callback_query(MasterFlow.wm_editing, F.data == "wm:closeall")
async def wm_close_all(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    booked = set(data.get("wm_booked", []))
    await state.update_data(wm_blocked=[t for t in TIME_SLOTS if t not in booked])
    await _render_grid(callback, state)
    await callback.answer("Усі вікна закрито")


@router.callback_query(MasterFlow.wm_editing, F.data == "wm:openall")
async def wm_open_all(callback: CallbackQuery, state: FSMContext):
    await state.update_data(wm_blocked=[])
    await _render_grid(callback, state)
    await callback.answer("Усі вікна відкрито")


@router.callback_query(MasterFlow.wm_editing, F.data == "wm:save")
async def wm_save(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    new_blocked = set(data.get("wm_blocked", []))
    original    = data.get("wm_original", {})
    service     = data["wm_service"]
    date_str    = data["wm_date"]

    await save_blocked_slots(date_str, service, new_blocked, original)
    await state.clear()
    await callback.message.edit_text(
        texts.master_wm_saved(service, _date_ua(date_str), len(new_blocked)),
        reply_markup=back_to_master_kb(),
        parse_mode="HTML",
    )
    await callback.answer("Збережено ✅")


# ══════════════════════════════════════════════════════════
#  ЕТАП 3 — СКИДКОВІ ВІКНА
# ══════════════════════════════════════════════════════════
import anthropic
from states import DiscountFlow, MasterAIFlow
from keyboards import (discount_menu_kb, discount_service_kb, discount_time_kb,
                       discount_percent_kb, discount_list_kb, master_ai_kb)
from config import ANTHROPIC_API_KEY
from utils.sheets import (get_available_times, add_discount,
                          get_discounts, delete_discount)


@router.callback_query(F.data == "master:discounts")
async def discounts_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        texts.DISCOUNT_MENU, reply_markup=discount_menu_kb(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "disc:add")
async def disc_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DiscountFlow.choosing_service)
    await callback.message.edit_text(
        texts.DISCOUNT_PICK_SERVICE, reply_markup=discount_service_kb(), parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(DiscountFlow.choosing_service, F.data.startswith("dsvc:"))
async def disc_service(callback: CallbackQuery, state: FSMContext):
    svc = callback.data.split(":", 1)[1]
    service_name = "Манікюр" if svc == "manicure" else "Педикюр"
    await state.update_data(disc_service=service_name)
    await state.set_state(DiscountFlow.choosing_date)
    await callback.message.edit_text(
        texts.discount_pick_date(service_name),
        reply_markup=master_date_kb("ddate"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(DiscountFlow.choosing_date, F.data.startswith("ddate:"))
async def disc_date(callback: CallbackQuery, state: FSMContext):
    date_str = callback.data.split(":", 1)[1]
    data = await state.get_data()
    service = data["disc_service"]
    available = await get_available_times(date_str, service)

    if not available:
        await callback.message.edit_text(
            texts.DISCOUNT_NO_SLOTS, reply_markup=master_date_kb("ddate"), parse_mode="HTML"
        )
        await callback.answer()
        return

    await state.update_data(disc_date=date_str)
    await state.set_state(DiscountFlow.choosing_time)
    await callback.message.edit_text(
        texts.discount_pick_time(service, _date_ua(date_str)),
        reply_markup=discount_time_kb(available),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(DiscountFlow.choosing_time, F.data.startswith("dtime:"))
async def disc_time(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.split(":", 1)[1]
    data = await state.get_data()
    await state.update_data(disc_time=time_str)
    await state.set_state(DiscountFlow.choosing_percent)
    await callback.message.edit_text(
        texts.discount_pick_percent(data["disc_service"], _date_ua(data["disc_date"]), time_str),
        reply_markup=discount_percent_kb(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(DiscountFlow.choosing_percent, F.data.startswith("dpct:"))
async def disc_percent(callback: CallbackQuery, state: FSMContext):
    percent = int(callback.data.split(":", 1)[1])
    data = await state.get_data()
    await add_discount(data["disc_date"], data["disc_time"], data["disc_service"], percent)
    await state.clear()
    await callback.message.edit_text(
        texts.discount_saved(data["disc_service"], _date_ua(data["disc_date"]),
                             data["disc_time"], percent),
        reply_markup=back_to_master_kb(),
        parse_mode="HTML",
    )
    await callback.answer("Знижку додано ✅")


@router.callback_query(F.data == "disc:list")
async def disc_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    discounts = await get_discounts()
    if not discounts:
        await callback.message.edit_text(
            texts.DISCOUNT_LIST_EMPTY, reply_markup=discount_menu_kb(), parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            texts.DISCOUNT_LIST_HEADER, reply_markup=discount_list_kb(discounts), parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("ddel:"))
async def disc_delete(callback: CallbackQuery, state: FSMContext):
    record_id = callback.data.split(":", 1)[1]
    await delete_discount(record_id)
    discounts = await get_discounts()
    if not discounts:
        await callback.message.edit_text(
            texts.DISCOUNT_LIST_EMPTY, reply_markup=discount_menu_kb(), parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            texts.DISCOUNT_LIST_HEADER, reply_markup=discount_list_kb(discounts), parse_mode="HTML"
        )
    await callback.answer(texts.DISCOUNT_DELETED)


# ══════════════════════════════════════════════════════════
#  ЕТАП 3 — ІІ ПОМІЧНИК ПО БОТУ (для майстра)
# ══════════════════════════════════════════════════════════
MASTER_AI_SYSTEM = """Ти — помічник для майстра салону краси Beauty & Shine.
Ти пояснюєш як користуватись Telegram-ботом салону.

Можливості бота в панелі майстра:
- 📋 «Історія за день» — переглянути всі записи на будь-яку дату з сумою виторгу.
- 🗓 «Менеджмент вікон» — закрити або відкрити часові слоти. Окремо для манікюру та педикюру. Є кнопки «Закрити весь день» і «Відкрити весь день». Закриті слоти клієнт бачить як недоступні.
- 🎁 «Скидкові вікна» — призначити знижку на конкретний вільний слот. Клієнт бачить знижку і вона застосовується автоматично при записі.
- 🔧 «Тех. режим» — тимчасово вимкнути бота для клієнтів (вони бачитимуть повідомлення про технічні роботи).

Правила:
- Відповідай ВИКЛЮЧНО українською мовою.
- Коротко, по суті, дружньо. Максимум 4-5 речень.
- Якщо питання не стосується бота — ввічливо поясни що допомагаєш лише з ботом."""


@router.callback_query(F.data == "master:ai")
async def master_ai_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(MasterAIFlow.asking)
    await callback.message.edit_text(
        texts.MASTER_AI_INTRO, reply_markup=master_ai_kb(), parse_mode="HTML"
    )
    await callback.answer()


@router.message(MasterAIFlow.asking)
async def master_ai_answer(message: Message, state: FSMContext):
    question = message.text or ""
    thinking = await message.answer(texts.MASTER_AI_THINKING)
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=MASTER_AI_SYSTEM,
            messages=[{"role": "user", "content": question}],
        )
        answer = resp.content[0].text
    except Exception:
        answer = "Технічна помилка. Спробуйте ще раз трохи пізніше."
    await thinking.delete()
    await message.answer(
        texts.master_ai_answer(answer), reply_markup=master_ai_kb(), parse_mode="HTML"
    )
    # стан лишається MasterAIFlow.asking — можна питати далі
