from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states import CallbackFlow
from keyboards import back_to_menu_kb
from utils.sheets import save_callback
from utils.notifications import notify_ivan_callback
import texts

router = Router()


@router.callback_query(F.data == "svc:callback")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CallbackFlow.entering_phone)
    await callback.message.edit_text(texts.CALLBACK_INTRO, parse_mode="HTML")
    await callback.answer()


@router.message(CallbackFlow.entering_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = message.text or ""
    await state.update_data(phone=phone)
    await state.set_state(CallbackFlow.entering_question)
    await message.answer(texts.CALLBACK_QUESTION, parse_mode="HTML")


@router.message(CallbackFlow.entering_question)
@router.message(Command("skip"), CallbackFlow.entering_question)
async def get_question(message: Message, state: FSMContext):
    question = "" if message.text == "/skip" else (message.text or "")
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
    await message.answer(texts.CALLBACK_CONFIRMED, reply_markup=back_to_menu_kb(), parse_mode="HTML")
