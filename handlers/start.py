"""Стартовий хаб бота: /start, навігація клієнта.

Модель UX (гібрид):
  • Нижня reply-клавіатура — ПОВНЕ меню клієнта (як звично користувачам).
  • У чаті живе ОДНЕ «вікно» — фото-повідомлення, яке бот редагує при
    кожному переході. Повідомлення-натискання reply-кнопок видаляються,
    тож чат не засмічується.
  • Термінальні повідомлення (лишаються в історії): картка запису,
    відповіді ШІ, підтвердження заявки на дзвінок, картка локації.

Майстер-режим — стара логіка master.py (не змінювався).
"""
import os
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from keyboards import (
    BTN, role_reply_kb, client_reply_kb,
    manicure_types_kb, pedicure_start_kb, screen_back_kb, call_cancel_kb,
)
from states import ManicureFlow, PedicureFlow, AIHelperFlow, CallbackFlow
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
async def update_window(bot: Bot, chat_id: int, photo_path: str, caption: str,
                        kb=None, reply_kb=None):
    """Оновлює вікно чату: редагує існуюче (фото+caption) або створює нове.
    reply_kb застосовується лише при створенні нового вікна."""
    mid = ui_state.get_window(chat_id)
    if mid:
        try:
            if os.path.exists(photo_path):
                await bot.edit_message_media(
                    chat_id=chat_id, message_id=mid,
                    media=InputMediaPhoto(media=FSInputFile(photo_path),
                                          caption=caption, parse_mode="HTML"),
                    reply_markup=kb,
                )
            else:
                await bot.edit_message_caption(
                    chat_id=chat_id, message_id=mid,
                    caption=caption, reply_markup=kb, parse_mode="HTML",
                )
            return
        except Exception:
            pass  # не вдалося редагувати — створюємо нове нижче

    await ui_state.delete_window(bot, chat_id)
    if os.path.exists(photo_path):
        m = await bot.send_photo(chat_id=chat_id, photo=FSInputFile(photo_path),
                                 caption=caption, reply_markup=kb or reply_kb,
                                 parse_mode="HTML")
    else:
        m = await bot.send_message(chat_id=chat_id, text=caption,
                                   reply_markup=kb or reply_kb, parse_mode="HTML")
    ui_state.set_window(chat_id, m.message_id)


async def _menu_caption(chat_id: int, user_id: int) -> str:
    user = await get_user_by_tg_id(user_id)
    profile = await get_client_profile(chat_id)
    if user:
        visits_count = profile["visits"] if profile else 0
        return texts.profile_card_text(user, visits_count)
    return texts.client_menu_text(profile)


async def show_menu_window(bot: Bot, chat_id: int, user_id: int, state: FSMContext,
                           force_new: bool = False):
    """Головне меню у вікні. force_new — надіслати новим повідомленням
    (після термінальних карток, щоб меню було знизу).
    Нове вікно ЗАВЖДИ йде з клієнтською reply-клавіатурою — гарантія,
    що нижні кнопки не зникнуть після будь-якого флоу."""
    await state.clear()
    if force_new:
        await ui_state.delete_window(bot, chat_id)
        ui_state.forget_window(chat_id)
    if is_maintenance():
        await update_window(bot, chat_id, MAINTENANCE_PATH, texts.MAINTENANCE,
                            reply_kb=client_reply_kb())
        return
    caption = await _menu_caption(chat_id, user_id)
    await update_window(bot, chat_id, MAIN_MENU_PATH, caption,
                        reply_kb=client_reply_kb())


# Сумісність зі старими викликами з manicure.py / pedicure.py
async def show_menu_new_window(bot: Bot, chat_id: int, user_id: int, state: FSMContext):
    await show_menu_window(bot, chat_id, user_id, state, force_new=True)


async def show_menu_in_window(callback: CallbackQuery, state: FSMContext):
    await show_menu_window(callback.bot, callback.message.chat.id,
                           callback.from_user.id, state)


async def _del(message: Message):
    """Тихо видаляє повідомлення-натискання reply-кнопки."""
    try:
        await message.delete()
    except Exception:
        pass


# ═══ /start ══════════════════════════════════════════════
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await ui_state.delete_window(message.bot, message.chat.id)
    if os.path.exists(BANNER_PATH):
        m = await message.answer_photo(
            photo=FSInputFile(BANNER_PATH),
            caption=texts.WELCOME_BANNER_CAPTION,
            reply_markup=role_reply_kb(),
            parse_mode="HTML",
        )
    else:
        m = await message.answer(texts.WELCOME_BANNER_CAPTION,
                                 reply_markup=role_reply_kb(), parse_mode="HTML")
    ui_state.set_window(message.chat.id, m.message_id)


# ═══ «Я клієнт» / «На початок» (reply) ═══════════════════
@router.message(F.text == BTN["client"])
async def btn_client(message: Message, state: FSMContext):
    await _del(message)
    await state.clear()
    # Ставимо клієнтську reply-клавіатуру разом з НОВИМ вікном меню
    await ui_state.delete_window(message.bot, message.chat.id)
    if is_maintenance():
        caption, photo = texts.MAINTENANCE, MAINTENANCE_PATH
    else:
        caption = await _menu_caption(message.chat.id, message.from_user.id)
        photo = MAIN_MENU_PATH
    if os.path.exists(photo):
        m = await message.answer_photo(photo=FSInputFile(photo), caption=caption,
                                       reply_markup=client_reply_kb(), parse_mode="HTML")
    else:
        m = await message.answer(caption, reply_markup=client_reply_kb(), parse_mode="HTML")
    ui_state.set_window(message.chat.id, m.message_id)


@router.message(F.text.in_({BTN["home"], BTN["menu"]}))
async def btn_home(message: Message, state: FSMContext):
    await _del(message)
    await state.clear()
    # Повернення до вибору ролі — нове вікно-банер з role-клавіатурою
    await ui_state.delete_window(message.bot, message.chat.id)
    if os.path.exists(BANNER_PATH):
        m = await message.answer_photo(photo=FSInputFile(BANNER_PATH),
                                       caption=texts.ROLE_SELECT,
                                       reply_markup=role_reply_kb(), parse_mode="HTML")
    else:
        m = await message.answer(texts.ROLE_SELECT, reply_markup=role_reply_kb(),
                                 parse_mode="HTML")
    ui_state.set_window(message.chat.id, m.message_id)


# ═══ Кнопки меню клієнта (reply → редагують вікно) ═══════
async def _maint_guard_msg(message: Message) -> bool:
    if is_maintenance():
        await update_window(message.bot, message.chat.id, MAINTENANCE_PATH, texts.MAINTENANCE)
        return True
    return False


@router.message(F.text == BTN["manicure"])
async def btn_manicure(message: Message, state: FSMContext):
    await _del(message)
    if await _maint_guard_msg(message):
        return
    await state.clear()
    await state.set_state(ManicureFlow.choosing_type)
    await update_window(message.bot, message.chat.id, IRINA_PATH,
                        texts.MANICURE_INTRO, manicure_types_kb())


@router.message(F.text == BTN["pedicure"])
async def btn_pedicure(message: Message, state: FSMContext):
    await _del(message)
    if await _maint_guard_msg(message):
        return
    await state.clear()
    await state.set_state(PedicureFlow.choosing_action)
    await update_window(message.bot, message.chat.id, IVAN_PATH,
                        texts.PEDICURE_INTRO, pedicure_start_kb())


@router.message(F.text == BTN["my_orders"])
async def btn_my_orders(message: Message, state: FSMContext):
    await _del(message)
    if await _maint_guard_msg(message):
        return
    await state.clear()
    orders = await get_recent_orders(message.from_user.id, days=7)
    await update_window(message.bot, message.chat.id, MAIN_MENU_PATH,
                        texts.orders_list_text(orders), screen_back_kb())


@router.message(F.text == BTN["my_visits"])
async def btn_my_visits(message: Message, state: FSMContext):
    await _del(message)
    if await _maint_guard_msg(message):
        return
    await state.clear()
    visits = await get_upcoming_visits(message.chat.id)
    await update_window(message.bot, message.chat.id, MAIN_MENU_PATH,
                        texts.visits_list_text(visits), screen_back_kb())


@router.message(F.text == BTN["sale"])
async def btn_sale(message: Message, state: FSMContext):
    await _del(message)
    if await _maint_guard_msg(message):
        return
    await state.clear()
    discounts = await get_discounts()
    await update_window(message.bot, message.chat.id, MAIN_MENU_PATH,
                        texts.client_discounts_text(discounts), screen_back_kb())


@router.message(F.text == BTN["ai"])
async def btn_ai(message: Message, state: FSMContext):
    await _del(message)
    if await _maint_guard_msg(message):
        return
    await state.set_state(AIHelperFlow.describing)
    await update_window(message.bot, message.chat.id, MAIN_MENU_PATH,
                        texts.AI_INTRO, screen_back_kb())


@router.message(F.text == BTN["call"])
async def btn_call(message: Message, state: FSMContext):
    await _del(message)
    if await _maint_guard_msg(message):
        return
    await state.set_state(CallbackFlow.entering_phone)
    await update_window(message.bot, message.chat.id, MAIN_MENU_PATH,
                        texts.CALLBACK_INTRO, call_cancel_kb())


# ═══ Inline-callbacks (екрани вікна) ═════════════════════
@router.callback_query(F.data == "nav:menu")
async def cb_nav_menu(callback: CallbackQuery, state: FSMContext):
    await show_menu_in_window(callback, state)
    await callback.answer()


@router.callback_query(F.data == "go:menu")
async def cb_go_menu(callback: CallbackQuery, state: FSMContext):
    await show_menu_in_window(callback, state)
    await callback.answer()


@router.callback_query(F.data == "ai:exit")
async def cb_ai_exit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await show_menu_window(callback.bot, callback.message.chat.id,
                           callback.from_user.id, state, force_new=True)
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


# Legacy: inline-кнопки ролей зі старого банера (якщо висить у когось)
@router.callback_query(F.data == "role:client")
async def cb_role_client(callback: CallbackQuery, state: FSMContext):
    await show_menu_in_window(callback, state)
    await callback.answer()


@router.callback_query(F.data == "role:master")
async def cb_role_master(callback: CallbackQuery, state: FSMContext):
    from states import MasterAuth
    await state.set_state(MasterAuth.entering_password)
    await update_window(callback.bot, callback.message.chat.id, BANNER_PATH,
                        texts.MASTER_PASSWORD_PROMPT)
    await callback.answer()


# Legacy svc:* — входи з нагадувань (reminders.py)
@router.callback_query(F.data == "svc:manicure")
async def cb_svc_manicure(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(ManicureFlow.choosing_type)
    await update_window(callback.bot, callback.message.chat.id, IRINA_PATH,
                        texts.MANICURE_INTRO, manicure_types_kb())
    await callback.answer()


@router.callback_query(F.data == "svc:pedicure")
async def cb_svc_pedicure(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(PedicureFlow.choosing_action)
    await update_window(callback.bot, callback.message.chat.id, IVAN_PATH,
                        texts.PEDICURE_INTRO, pedicure_start_kb())
    await callback.answer()


# ═══ Команди ═════════════════════════════════════════════
@router.message(Command("ai"))
async def cmd_ai(message: Message, state: FSMContext):
    await state.set_state(AIHelperFlow.describing)
    await update_window(message.bot, message.chat.id, MAIN_MENU_PATH,
                        texts.AI_INTRO, screen_back_kb())


@router.message(Command("skidky"))
async def cmd_skidky(message: Message, state: FSMContext):
    await state.clear()
    discounts = await get_discounts()
    await update_window(message.bot, message.chat.id, MAIN_MENU_PATH,
                        texts.client_discounts_text(discounts), screen_back_kb())


@router.message(Command("zapys"))
async def cmd_zapys(message: Message, state: FSMContext):
    await show_menu_window(message.bot, message.chat.id, message.from_user.id, state)


@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await message.answer(texts.HELP_TEXT, parse_mode="HTML")
