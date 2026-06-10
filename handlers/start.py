"""Стартовий хаб бота: /start, команди, головне меню клієнта, перемикач ролей.
Reply-клавіатура (нижнє меню) — це глобальна навігація, як у Westelecom.
Кнопки меню перехоплюються тут ПЕРШИМИ (роутер реєструється першим у bot.py),
тому вони працюють як «escape hatch» з будь-якого стану."""
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards import (
    role_reply_kb, client_reply_kb, remove_kb, BTN,
    manicure_types_kb, pedicure_start_kb,
)
from states import ManicureFlow, PedicureFlow, AIHelperFlow, CallbackFlow
from utils.settings import is_maintenance
from utils.sheets import get_client_profile, get_discounts, get_user_by_tg_id, get_recent_orders, get_upcoming_visits
import texts

router = Router()

BANNER_PATH      = "assets/welcome_banner.jpg"
MAIN_MENU_PATH   = "assets/main_menu.jpg"
MAINTENANCE_PATH = "assets/maintenance.jpg"
IRINA_PATH       = "assets/master_irina.jpg"
IVAN_PATH        = "assets/master_ivan.jpg"


# ── Допоміжні: показ тех-режиму, головного меню ──────────
async def _show_maintenance(message: Message):
    """Текст + картинка тех-режиму."""
    if os.path.exists(MAINTENANCE_PATH):
        await message.answer_photo(
            photo=FSInputFile(MAINTENANCE_PATH),
            caption=texts.MAINTENANCE,
            reply_markup=remove_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(texts.MAINTENANCE, reply_markup=remove_kb(), parse_mode="HTML")


async def show_client_menu(message: Message, state: FSMContext):
    """Показує клієнтське меню з персоналізацією.
    Якщо юзер зареєстрований на сайті — повна картка профілю з бонусами."""
    await state.clear()
    if is_maintenance():
        await _show_maintenance(message)
        return
    # Пробуємо знайти юзера в таблиці «Користувачі» (сайт-реєстрація)
    user = await get_user_by_tg_id(message.from_user.id)
    if user:
        # Юзер є на сайті → показуємо розширену картку з бонусами
        profile = await get_client_profile(message.chat.id)
        visits_count = profile["visits"] if profile else 0
        caption = texts.profile_card_text(user, visits_count)
    else:
        # Юзер тільки в боті → стара логіка
        profile = await get_client_profile(message.chat.id)
        caption = texts.client_menu_text(profile)
    if os.path.exists(MAIN_MENU_PATH):
        await message.answer_photo(
            photo=FSInputFile(MAIN_MENU_PATH),
            caption=caption,
            reply_markup=client_reply_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(caption, reply_markup=client_reply_kb(), parse_mode="HTML")


# ══ /start ═════════════════════════════════════════════
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    if os.path.exists(BANNER_PATH):
        await message.answer_photo(
            photo=FSInputFile(BANNER_PATH),
            caption=texts.WELCOME_BANNER_CAPTION,
            reply_markup=role_reply_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            texts.WELCOME_BANNER_CAPTION,
            reply_markup=role_reply_kb(),
            parse_mode="HTML",
        )


# ══ Кнопки ролей (нижнє меню) ══════════════════════════
@router.message(F.text == BTN["client"])
async def btn_client(message: Message, state: FSMContext):
    await show_client_menu(message, state)


@router.message(F.text == BTN["home"])
async def btn_home(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        texts.ROLE_SELECT,
        reply_markup=role_reply_kb(),
        parse_mode="HTML",
    )


# ══ Кнопки головного меню → старт відповідного флоу ════
async def _check_maint_or(message: Message) -> bool:
    """True якщо тех-режим (вже показали повідомлення). Інакше False."""
    if is_maintenance():
        await _show_maintenance(message)
        return True
    return False


@router.message(F.text == BTN["manicure"])
async def btn_manicure(message: Message, state: FSMContext):
    if await _check_maint_or(message):
        return
    await state.clear()
    await state.set_state(ManicureFlow.choosing_type)
    if os.path.exists(IRINA_PATH):
        await message.answer_photo(
            photo=FSInputFile(IRINA_PATH),
            caption=texts.MANICURE_INTRO,
            reply_markup=manicure_types_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            texts.MANICURE_INTRO,
            reply_markup=manicure_types_kb(),
            parse_mode="HTML",
        )


@router.message(F.text == BTN["pedicure"])
async def btn_pedicure(message: Message, state: FSMContext):
    if await _check_maint_or(message):
        return
    await state.clear()
    await state.set_state(PedicureFlow.choosing_action)
    if os.path.exists(IVAN_PATH):
        await message.answer_photo(
            photo=FSInputFile(IVAN_PATH),
            caption=texts.PEDICURE_INTRO,
            reply_markup=pedicure_start_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            texts.PEDICURE_INTRO,
            reply_markup=pedicure_start_kb(),
            parse_mode="HTML",
        )


@router.message(F.text == BTN["ai"])
async def btn_ai(message: Message, state: FSMContext):
    if await _check_maint_or(message):
        return
    await state.set_state(AIHelperFlow.describing)
    await message.answer(texts.AI_INTRO, parse_mode="HTML")


@router.message(F.text == BTN["call"])
async def btn_call(message: Message, state: FSMContext):
    if await _check_maint_or(message):
        return
    await state.set_state(CallbackFlow.entering_phone)
    await message.answer(texts.CALLBACK_INTRO, parse_mode="HTML")


@router.message(F.text == BTN["sale"])
async def btn_sale(message: Message, state: FSMContext):
    if await _check_maint_or(message):
        return
    await state.clear()
    discounts = await get_discounts()
    await message.answer(
        texts.client_discounts_text(discounts),
        parse_mode="HTML",
    )


@router.message(F.text == BTN["my_orders"])
async def btn_my_orders(message: Message, state: FSMContext):
    """Останні замовлення з сайту за 7 днів."""
    if await _check_maint_or(message):
        return
    await state.clear()
    orders = await get_recent_orders(message.from_user.id, days=7)
    await message.answer(texts.orders_list_text(orders), parse_mode="HTML", disable_web_page_preview=True)


@router.message(F.text == BTN["my_visits"])
async def btn_my_visits(message: Message, state: FSMContext):
    """Майбутні записи на процедури."""
    if await _check_maint_or(message):
        return
    await state.clear()
    visits = await get_upcoming_visits(message.chat.id)
    await message.answer(texts.visits_list_text(visits), parse_mode="HTML", disable_web_page_preview=True)


# ══ Команди (швидкий запуск з меню «/») ════════════════
@router.message(Command("ai"))
async def cmd_ai(message: Message, state: FSMContext):
    await btn_ai(message, state)


@router.message(Command("skidky"))
async def cmd_skidky(message: Message, state: FSMContext):
    await btn_sale(message, state)


@router.message(Command("zapys"))
async def cmd_zapys(message: Message, state: FSMContext):
    await show_client_menu(message, state)


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer(texts.HELP_TEXT, parse_mode="HTML")


# ══ Callback-навігація (для inline-кнопок у флоу) ══════
@router.callback_query(F.data == "go:menu")
async def cb_go_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    # головне меню — нове повідомлення (бо попереднє могло бути фото з caption)
    await show_client_menu(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


# Legacy svc:* callbacks — для inline-входів з інших місць
@router.callback_query(F.data == "svc:manicure")
async def cb_svc_manicure(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ManicureFlow.choosing_type)
    if os.path.exists(IRINA_PATH):
        await callback.message.answer_photo(
            photo=FSInputFile(IRINA_PATH),
            caption=texts.MANICURE_INTRO,
            reply_markup=manicure_types_kb(),
            parse_mode="HTML",
        )
    else:
        await callback.message.answer(
            texts.MANICURE_INTRO,
            reply_markup=manicure_types_kb(),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data == "svc:pedicure")
async def cb_svc_pedicure(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PedicureFlow.choosing_action)
    if os.path.exists(IVAN_PATH):
        await callback.message.answer_photo(
            photo=FSInputFile(IVAN_PATH),
            caption=texts.PEDICURE_INTRO,
            reply_markup=pedicure_start_kb(),
            parse_mode="HTML",
        )
    else:
        await callback.message.answer(
            texts.PEDICURE_INTRO,
            reply_markup=pedicure_start_kb(),
            parse_mode="HTML",
        )
    await callback.answer()
