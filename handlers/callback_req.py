"""Дзвінок майстра. Вхід — у start.py (btn_call). Тут лише обробка телефону й питання."""
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import CallbackFlow
from keyboards import back_to_menu_kb
from utils.sheets import save_callback
from utils.notifications import notify_ivan_callback
import texts

router = Router()


@router.message(CallbackFlow.entering_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = (message.text or "").strip()
    await state.update_data(phone=phone)
    await state.set_state(CallbackFlow.entering_question)
    await message.answer(texts.CALLBACK_QUESTION, parse_mode="HTML")


@router.message(CallbackFlow.entering_question)
async def get_question(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    question = "" if raw == "/skip" else raw
    data = await state.get_data()
    user = message.from_user

    await save_callback(
        client_name=user.full_name, client_username=user.username or "",
        phone=data.get("phone", "—"), question=question,
    )
    await notify_ivan_callback(
        bot=message.bot,
        client_name=user.full_name, client_username=user.username,
        phone=data.get("phone", "—"), question=question,
    )
    await state.clear()
    await message.answer(
        texts.CALLBACK_CONFIRMED, reply_markup=back_to_menu_kb(), parse_mode="HTML"
    )
