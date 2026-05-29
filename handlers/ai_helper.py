"""ШІ помічник для клієнта. Покращений промт: природна українська, без кальки.
Вхід — у start.py (btn_ai). Тут лише обробка відповіді."""
import anthropic
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import AIHelperFlow
from utils.notifications import notify_ivan_ai_alert
from config import ANTHROPIC_API_KEY
import texts

router = Router()

# Покращений системний промт: акцент на природну професійну українську,
# а не дослівний переклад з російської / іншої мови.
AI_SYSTEM_PROMPT = """Ти — ШІ-помічник салону краси та здоров'я Beauty & Shine в Ізмаїлі.
Ти спеціалізуєшся на догляді за руками й ногами — манікюр, педикюр, подологія.

МОВА (критично важливо):
- Відповідай ВИКЛЮЧНО українською мовою — природною, живою, фаховою.
- Не перекладай дослівно з російської. Думай і пиши українською з нуля.
- Користуйся справжніми українськими термінами догляду:
  «нігтьова пластина», «кутикула», «огрубіла шкіра», «врослий ніготь»,
  «нігтьовий валик», «загартування», «пом'якшення», а не калькованими.
- Не використовуй русизми («ногті», «врости», «нарощування ногтей»).
  Пиши «нігті», «врости в шкіру», «нарощування нігтів».
- Стиль — теплий, доброзичливий, професійний. Як майстер пояснює клієнту.

ЗМІСТ ВІДПОВІДІ:
1. Якщо клієнт описує медичну проблему (врослий ніготь, грибок, запалення,
   сильний біль, набряк, ранка) — дай 2-3 практичні поради як полегшити стан
   та обов'язково порадь звернутись до подолога Івана.
2. Якщо звичайне питання догляду — поясни просто й коротко, без води.
3. Максимум 4 речення.
4. Закінчуй пропозицією записатись або замовити дзвінок-консультацію.

НЕ давай медичних діагнозів. У серйозних випадках — направляй до майстра."""

NEEDS_ALERT_KEYWORDS = [
    "врослий", "вросений", "вросший", "гриб", "запалення", "запалений",
    "гній", "набряк", "сильний біль", "кров", "рана", "ранка",
]


def _needs_alert(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in NEEDS_ALERT_KEYWORDS)


@router.message(AIHelperFlow.describing)
async def handle_problem(message: Message, state: FSMContext):
    problem = message.text or ""
    thinking_msg = await message.answer(texts.AI_THINKING)
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=AI_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": problem}],
        )
        answer = response.content[0].text
    except Exception:
        answer = ("На жаль, виникла технічна помилка. "
                  "Спробуйте ще раз або скористайтесь кнопкою «Дзвінок майстра» внизу.")
    await thinking_msg.delete()
    # Без inline-кнопок — наша reply-клавіатура внизу має все потрібне (Манікюр, Педикюр, Дзвінок, На початок)
    await message.answer(texts.ai_response_text(answer), parse_mode="HTML")

    # Якщо в описі — медичні ключові слова, надсилаємо алерт Івану
    if _needs_alert(problem):
        await notify_ivan_ai_alert(
            bot=message.bot,
            client_name=message.from_user.full_name,
            client_username=message.from_user.username,
            symptom=problem,
            ai_summary=answer[:300],
        )

    # Стан лишається — клієнт може ставити нові питання, або вийти через нижні кнопки
