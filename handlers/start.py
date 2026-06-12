"""Стартовий хаб бота: /start, вікно-навігація клієнта (новий edit-message UX).

Модель: на чат існує ОДНЕ «вікно» — фото-повідомлення з caption та inline-
кнопками. Уся навігація редагує це вікно (edit_message_media / edit_caption)
замість надсилання нових повідомлень.

Термінальні повідомлення (лишаються в історії як результат):
  • картка підтвердженого запису (manicure.py / pedicure.py)
  • відповіді ШІ-помічника (ai_helper.py)
  • підтвердження запиту на дзвінок (callback_req.py)

Reply-клавіатура внизу — одна кнопка «🏠 Меню» (страховка).
Майстер-режим лишається на старій reply-логіці (master.py не змінювався).
"""
import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards import (
    BTN, home_reply_kb, role_inline_kb, client_menu_inline_kb,
    screen_back_kb, call_cancel_kb, role_reply_kb,
    manicure_types_kb, pedicure_start_kb,
)
from states import ManicureFlow, PedicureFlow, AIHelperFlow, CallbackFlow, MasterAuth
from utils.settings import is_maintenance
from utils.sheets import (
    get_client_profile, get_discounts, get_user_by_tg_id,
    get_recent_orders, get_upcoming_visits,
)
from utils import ui_state
import texts

router = Router()

BANNER_PATH      = "assets/welcome_banner.jpg"
MAIN_MENU_PATH   = "assets/main_menu.jpg"
MAINTENANCE_PATH = "assets/maintenance.jpg"
IRINA_PATH       = "assets/master_irina.jpg"
IVAN_PATH        = "assets/master_ivan.jpg"


# ═══ Хелпери вікна ═══════════════════════════════════════
def _media(path: str, caption: str, fallback_caption_only=False) -> InputMediaPhoto | None:
    if os.path.exists(path):
        return InputMediaPhoto(media=FSInputFile(path), caption=caption, parse_mode="HTML")
    return None


async def _edit_window(callback: CallbackQuery, photo_path: str, caption: str, kb=None):
    """Редагує вікно: міняє фото+caption (edit_media) або тільки caption."""
    msg = callback.message
    media = _media(photo_path, caption)
    try:
        if media and msg.photo:
            await msg.edit_media(media=media, reply_markup=kb)
        elif msg.photo:
            await msg.edit_caption(caption=caption, reply_markup=kb, parse_mode="HTML")
        else:
            await msg.edit_text(caption, reply_markup=kb, parse_mode="HTML")
        ui_state.set_window(msg.chat.id, msg.message_id)
    except Exception:
        # Якщо редагування неможливе (повідомлення застаре) — нове вікно
        await send_new_window(callback.bot, msg.chat.id, photo_path, caption, kb)


async def send_new_window(bot: Bot, chat_id: int, photo_path: str, caption: str, kb=None):
    """Видаляє старе вікно і надсилає нове. Повертає message_id."""
    await ui_state.delete_window(bot, chat_id)
    if os.path.exists(photo_path):
        m = await bot.send_photo(
            chat_id=chat_id, photo=FSInputFile(photo_path),
            caption=caption, reply_markup=kb, parse_mode="HTML",
        )
    else:
        m = await bot.send_message(
            chat_id=chat_id, text=caption, reply_markup=kb, parse_mode="HTML",
        )
    ui_state.set_window(chat_id, m.message_id)
    return m.message_id


async def _menu_caption(chat_id: int, user_id: int) -> str:
    """Caption головного меню: повна картка якщо юзер з сайту, інакше базова."""
    user = await get_user_by_tg_id(user_id)
    profile = await get_client_profile(chat_id)
    if user:
        visits_count = profile["visits"] if profile else 0
        return texts.profile_card_text(user, visits_count)
    return texts.client_menu_text(profile)


async def show_menu_in_window(callback: CallbackQuery, state: FSMContext):
    """Редагує вікно у головне меню клієнта."""
    await state.clear()
    if is_maintenance():
        await _edit_window(callback, MAINTENANCE_PATH, texts.MAINTENANCE)
        return
    caption = await _menu_caption(callback.message.chat.id, callback.from_user.id)
    await _edit_window(callback, MAIN_MENU_PATH, caption, client_menu_inline_kb())


async def show_menu_new_window(bot: Bot, chat_id: int, user_id: int, state: FSMContext):
    """Надсилає НОВЕ вікно з головним меню (видаляючи старе)."""
    await state.clear()
    if is_maintenance():
        await send_new_window(bot, chat_id, MAINTENANCE_PATH, texts.MAINTENANCE)
        return
    caption = await _menu_caption(chat_id, user_id)
    await send_new_window(bot, chat_id, MAIN_MENU_PATH, caption, client_menu_inline_kb())


# ═══ /start ══════════════════════════════════════════════
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    # Reply-страховка «🏠 Меню» ставиться разом із банером
    await ui_state.delete_window(message.bot, message.chat.id)
    if os.path.exists(BANNER_PATH):
        m = await message.answer_photo(
            photo=FSInputFile(BANNER_PATH),
            caption=texts.WELCOME_BANNER_CAPTION,
            reply_markup=role_inline_kb(),
            parse_mode="HTML",
        )
    else:
        m = await message.answer(
            texts.WELCOME_BANNER_CAPTION,
            reply_markup=role_inline_kb(),
            parse_mode="HTML",
        )
    ui_state.set_window(message.chat.id, m.message_id)
    # окремо ставимо reply-клавіатуру (Telegram не дозволяє reply+inline в одному)
    await message.answer("👇", reply_markup=home_reply_kb(), disable_notification=True)


# ═══ Вибір ролі (inline у банері) ════════════════════════
@router.callback_query(F.data == "role:client")
async def cb_role_client(callback: CallbackQuery, state: FSMContext):
    await show_menu_in_window(callback, state)
    await callback.answer()


@router.callback_query(F.data == "role:master")
async def cb_role_master(callback: CallbackQuery, state: FSMContext):
    """Вхід у майстер-режим: питаємо пароль (далі — стара логіка master.py)."""
    await state.set_state(MasterAuth.entering_password)
    await _edit_window(callback, BANNER_PATH, texts.MASTER_PASSWORD_PROMPT)
    await callback.answer()


# ═══ Reply «🏠 Меню» (страховка) ═════════════════════════
@router.message(F.text == BTN["menu"])
async def btn_menu(message: Message, state: FSMContext):
    # видаляємо повідомлення юзера з кнопки, щоб не смітило
    try:
        await message.delete()
    except Exception:
        pass
    await show_menu_new_window(message.bot, message.chat.id, message.from_user.id, state)


# Старі reply-кнопки (якщо у когось лишилась стара клавіатура) — м'яка міграція
@router.message(F.text.in_({BTN["client"], BTN["home"]}))
async def btn_legacy_nav(message: Message, state: FSMContext):
    await show_menu_new_window(message.bot, message.chat.id, message.from_user.id, state)


# ═══ Inline-меню клієнта (екрани вікна) ══════════════════
async def _maint_guard(callback: CallbackQuery) -> bool:
    if is_maintenance():
        await _edit_window(callback, MAINTENANCE_PATH, texts.MAINTENANCE)
        await callback.answer()
        return True
    return False


@router.callback_query(F.data == "nav:menu")
async def cb_nav_menu(callback: CallbackQuery, state: FSMContext):
    await show_menu_in_window(callback, state)
    await callback.answer()


@router.callback_query(F.data == "menu:manicure")
async def cb_menu_manicure(callback: CallbackQuery, state: FSMContext):
    if await _maint_guard(callback):
        return
    await state.clear()
    await state.set_state(ManicureFlow.choosing_type)
    await _edit_window(callback, IRINA_PATH, texts.MANICURE_INTRO, manicure_types_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:pedicure")
async def cb_menu_pedicure(callback: CallbackQuery, state: FSMContext):
    if await _maint_guard(callback):
        return
    await state.clear()
    await state.set_state(PedicureFlow.choosing_action)
    await _edit_window(callback, IVAN_PATH, texts.PEDICURE_INTRO, pedicure_start_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:orders")
async def cb_menu_orders(callback: CallbackQuery, state: FSMContext):
    if await _maint_guard(callback):
        return
    await state.clear()
    orders = await get_recent_orders(callback.from_user.id, days=7)
    await _edit_window(callback, MAIN_MENU_PATH, texts.orders_list_text(orders), screen_back_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:visits")
async def cb_menu_visits(callback: CallbackQuery, state: FSMContext):
    if await _maint_guard(callback):
        return
    await state.clear()
    visits = await get_upcoming_visits(callback.message.chat.id)
    await _edit_window(callback, MAIN_MENU_PATH, texts.visits_list_text(visits), screen_back_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:sale")
async def cb_menu_sale(callback: CallbackQuery, state: FSMContext):
    if await _maint_guard(callback):
        return
    await state.clear()
    discounts = await get_discounts()
    await _edit_window(callback, MAIN_MENU_PATH, texts.client_discounts_text(discounts), screen_back_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:ai")
async def cb_menu_ai(callback: CallbackQuery, state: FSMContext):
    if await _maint_guard(callback):
        return
    await state.set_state(AIHelperFlow.describing)
    await _edit_window(callback, MAIN_MENU_PATH, texts.AI_INTRO, screen_back_kb())
    await callback.answer()


@router.callback_query(F.data == "menu:call")
async def cb_menu_call(callback: CallbackQuery, state: FSMContext):
    if await _maint_guard(callback):
        return
    await state.set_state(CallbackFlow.entering_phone)
    await _edit_window(callback, MAIN_MENU_PATH, texts.CALLBACK_INTRO, call_cancel_kb())
    await callback.answer()


# ═══ Завершення розмови з ШІ ═════════════════════════════
@router.callback_query(F.data == "ai:exit")
async def cb_ai_exit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    # прибираємо кнопку з останньої відповіді (відповідь лишається — термінальна)
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await show_menu_new_window(callback.bot, callback.message.chat.id, callback.from_user.id, state)
    await callback.answer()


# ═══ Команди (швидкий запуск з меню «/») ═════════════════
@router.message(Command("ai"))
async def cmd_ai(message: Message, state: FSMContext):
    await state.set_state(AIHelperFlow.describing)
    await send_new_window(message.bot, message.chat.id, MAIN_MENU_PATH, texts.AI_INTRO, screen_back_kb())


@router.message(Command("skidky"))
async def cmd_skidky(message: Message, state: FSMContext):
    await state.clear()
    discounts = await get_discounts()
    await send_new_window(message.bot, message.chat.id, MAIN_MENU_PATH,
                          texts.client_discounts_text(discounts), screen_back_kb())


@router.message(Command("zapys"))
async def cmd_zapys(message: Message, state: FSMContext):
    await show_menu_new_window(message.bot, message.chat.id, message.from_user.id, state)


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer(texts.HELP_TEXT, parse_mode="HTML")


# ═══ Службові callbacks ══════════════════════════════════
@router.callback_query(F.data == "go:menu")
async def cb_go_menu(callback: CallbackQuery, state: FSMContext):
    """Legacy: «← Меню» зі старих клавіатур (back_to_menu_kb у флоу запису)."""
    await show_menu_in_window(callback, state)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


# Legacy svc:* — входи з нагадувань (reminders.py)
@router.callback_query(F.data == "svc:manicure")
async def cb_svc_manicure(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ManicureFlow.choosing_type)
    await send_new_window(callback.bot, callback.message.chat.id,
                          IRINA_PATH, texts.MANICURE_INTRO, manicure_types_kb())
    await callback.answer()


@router.callback_query(F.data == "svc:pedicure")
async def cb_svc_pedicure(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PedicureFlow.choosing_action)
    await send_new_window(callback.bot, callback.message.chat.id,
                          IVAN_PATH, texts.PEDICURE_INTRO, pedicure_start_kb())
    await callback.answer()
