"""Дзвінок майстра (новий UX). Вхід — start.py (menu:call редагує вікно на CALLBACK_INTRO).
Юзер пише телефон і питання текстом (його повідомлення лишаються — це нормально),
бот між кроками редагує ВІКНО, а не плодить нові повідомлення.
Підтвердження — ТЕРМІНАЛЬНЕ повідомлення + нове вікно меню."""
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import CallbackFlow
from keyboards import call_cancel_kb
from utils.sheets import save_callback
from utils.notifications import notify_ivan_callback
from utils import ui_state
import texts

router = Router()


async def _edit_window_text(bot, chat_id: int, text: str, kb=None) -> bool:
    """Редагує caption вікна за збереженим id. True якщо вдалося."""
    mid = ui_state.get_window(chat_id)
    if not mid:
        return False
    try:
        await bot.edit_message_caption(
            chat_id=chat_id, message_id=mid,
            caption=text, reply_markup=kb, parse_mode="HTML",
        )
        return True
    except Exception:
        try:
            await bot.edit_message_text(
                chat_id=chat_id, message_id=mid,
                text=text, reply_markup=kb, parse_mode="HTML",
            )
            return True
        except Exception:
            return False


@router.message(CallbackFlow.entering_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = (message.text or "").strip()
    await state.update_data(phone=phone)
    await state.set_state(CallbackFlow.entering_question)
    # редагуємо вікно на наступний крок; якщо вікна нема — fallback нове повідомлення
    ok = await _edit_window_text(message.bot, message.chat.id, texts.CALLBACK_QUESTION, call_cancel_kb())
    if not ok:
        await message.answer(texts.CALLBACK_QUESTION, parse_mode="HTML")


@router.message(CallbackFlow.entering_question)
async def get_question(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    question = "" if raw == "/skip" else raw
    data = await state.get_data()
    user = message.from_user

    # Якщо заявка прийшла з педикюр-флоу — додаємо контекст для Івана
    ctx = data.get("consult_context", "")
    full_question = f"[{ctx}] {question}".strip() if ctx else question

    await save_callback(
        client_name=user.full_name, client_username=user.username or "",
        phone=data.get("phone", "—"), question=full_question,
    )
    await notify_ivan_callback(
        bot=message.bot,
        client_name=user.full_name, client_username=user.username,
        phone=data.get("phone", "—"), question=full_question,
    )
    await state.clear()
    # ТЕРМІНАЛЬНЕ підтвердження (лишається в історії)
    await message.answer(texts.CALLBACK_CONFIRMED, parse_mode="HTML")
    # Нове вікно з меню — знизу
    from handlers.start import show_menu_new_window
    await show_menu_new_window(message.bot, message.chat.id, message.from_user.id, state)
