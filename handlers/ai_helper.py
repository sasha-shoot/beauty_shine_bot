import anthropic
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import AIHelperFlow
from keyboards import ai_after_kb, back_to_menu_kb
from utils.notifications import notify_ivan_ai_alert
from config import ANTHROPIC_API_KEY
import texts

router = Router()

AI_SYSTEM_PROMPT = """Ти — ІІ-помічник салону краси та здоров'я Beauty & Shine в Ізмаїлі.
Ти спеціалізуєшся на підготовці клієнтів до процедур манікюру та педикюру.

Твої правила:
1. Відповідай ВИКЛЮЧНО українською мовою.
2. Будь теплим, доброзичливим та фаховим.
3. Якщо клієнт описує медичну проблему (вросший ніготь, грибок, запалення, сильний біль, набряк, ранка) — надай тимчасову пораду як полегшити стан і обов'язково рекомендуй звернутись до майстра-подолога Іван Петровича.
4. Надавай ПРАКТИЧНІ поради (підняти ногу, холодна вода, не давити, чиста пов'язка тощо).
5. Максимум 4 речення у відповіді.
6. Закінчуй відповідь пропозицією записатись або замовити дзвінок-консультацію.

ВАЖЛИВО: Не давай медичних діагнозів. Якщо ситуація серйозна — направляй до майстра."""

NEEDS_ALERT_KEYWORDS = [
    "вросший", "вросений", "гриб", "запалення", "запалений",
    "гній", "набряк", "сильний біль", "кров", "рана", "ранка"
]


def _needs_alert(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in NEEDS_ALERT_KEYWORDS)


@router.callback_query(F.data == "svc:ai")
async def start_ai(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AIHelperFlow.describing)
    await callback.message.edit_text(texts.AI_INTRO, parse_mode="HTML")
    await callback.answer()


@router.message(AIHelperFlow.describing)
async def handle_problem(message: Message, state: FSMContext):
    problem = message.text or ""
    await state.update_data(problem=problem)

    thinking_msg = await message.answer(texts.AI_THINKING)

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=AI_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": problem}]
        )
        answer = response.content[0].text
    except Exception:
        answer = ("На жаль, зараз виникла технічна помилка. "
                  "Будь ласка, зателефонуйте нам або залиште заявку на дзвінок.")

    await thinking_msg.delete()
    await message.answer(texts.ai_response_text(answer), reply_markup=ai_after_kb(), parse_mode="HTML")

    # Alert Ivan if medical keywords detected
    if _needs_alert(problem):
        await notify_ivan_ai_alert(
            bot=message.bot,
            client_name=message.from_user.full_name,
            client_username=message.from_user.username,
            symptom=problem,
            ai_summary=answer[:300],
        )

    await state.clear()
