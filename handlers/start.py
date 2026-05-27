import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards import role_select_kb, main_menu_kb, client_discounts_kb
from utils.settings import is_maintenance
import texts

router = Router()

BANNER_PATH = "assets/welcome_banner.jpg"


async def _present(callback: CallbackQuery, text: str, markup=None):
    """Якщо попереднє повідомлення — фото (банер), видаляємо і шлемо нове.
    Якщо звичайний текст — оновлюємо на місці. Так у чаті завжди один активний екран."""
    if callback.message.photo:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(text, reply_markup=markup, parse_mode="HTML")
    else:
        await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    if os.path.exists(BANNER_PATH):
        await message.answer_photo(
            photo=FSInputFile(BANNER_PATH),
            caption=texts.WELCOME_BANNER_CAPTION,
            reply_markup=role_select_kb(),
            parse_mode="HTML",
        )
    else:
        # Резервний варіант, якщо банер не знайдено
        await message.answer(
            texts.WELCOME_BANNER_CAPTION,
            reply_markup=role_select_kb(),
            parse_mode="HTML",
        )


@router.callback_query(F.data == "role:client")
async def role_client(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if is_maintenance():
        await _present(callback, texts.MAINTENANCE, None)
    else:
        await _present(callback, texts.WELCOME, main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "go:menu")
async def go_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if is_maintenance():
        await _present(callback, texts.MAINTENANCE, None)
    else:
        await _present(callback, texts.WELCOME, main_menu_kb())
    await callback.answer()


@router.callback_query(F.data == "go:start")
async def go_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    # «На початок» — текстова версія, без банера (банер тільки для /start)
    await _present(callback, texts.ROLE_SELECT, role_select_kb())
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "svc:discounts")
async def client_discounts(callback: CallbackQuery, state: FSMContext):
    from utils.sheets import get_discounts
    await state.clear()
    discounts = await get_discounts()
    await _present(
        callback,
        texts.client_discounts_text(discounts),
        client_discounts_kb(),
    )
    await callback.answer()
