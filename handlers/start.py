from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from keyboards import role_select_kb, main_menu_kb
from utils.settings import is_maintenance
import texts

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(texts.ROLE_SELECT, reply_markup=role_select_kb(), parse_mode="HTML")


async def _show_client_menu(callback: CallbackQuery):
    """Показує меню клієнта або повідомлення про тех-роботи."""
    if is_maintenance():
        await callback.message.edit_text(texts.MAINTENANCE, parse_mode="HTML")
    else:
        await callback.message.edit_text(texts.WELCOME, reply_markup=main_menu_kb(), parse_mode="HTML")


@router.callback_query(F.data == "role:client")
async def role_client(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await _show_client_menu(callback)
    await callback.answer()


@router.callback_query(F.data == "go:menu")
async def go_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await _show_client_menu(callback)
    await callback.answer()


@router.callback_query(F.data == "go:start")
async def go_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(texts.ROLE_SELECT, reply_markup=role_select_kb(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(F.data == "svc:discounts")
async def client_discounts(callback: CallbackQuery, state: FSMContext):
    from utils.sheets import get_discounts
    from keyboards import client_discounts_kb
    await state.clear()
    discounts = await get_discounts()
    await callback.message.edit_text(
        texts.client_discounts_text(discounts),
        reply_markup=client_discounts_kb(),
        parse_mode="HTML",
    )
    await callback.answer()
