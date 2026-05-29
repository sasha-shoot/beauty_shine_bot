# ══ ВХІД ════════════════════════════════════════════════
WELCOME_BANNER_CAPTION = (
    "✨ <b>Вітаємо у Beauty &amp; Shine!</b>\n\n"
    "Ми — сімейна студія краси та здоров'я в Ізмаїлі і "
    "<b>перший салон в Україні</b>, що пропонує своїм клієнтам "
    "повноцінного бот-помічника замість дзвінків та переписок.\n\n"
    "📱 <b>У цьому боті ви зможете:</b>\n"
    "💅 Записатись на манікюр чи педикюр\n"
    "🤖 Отримати ШІ-консультацію по догляду\n"
    "🎁 Знайти слоти зі знижкою\n"
    "📞 Замовити дзвінок майстра\n"
    "⏰ Отримувати нагадування про візит\n\n"
    "Усе в одному місці, без зайвих дзвінків і очікувань. 💜\n\n"
    "<b>Як бажаєте увійти?</b>"
)

ROLE_SELECT = (
    "✨ <b>Beauty &amp; Shine</b>\n\n"
    "Оберіть, як увійти:"
)

# ── Головне меню клієнта (підпис під картинкою main_menu) ──
def client_menu_text(profile: dict | None) -> str:
    """Картка клієнта з персоналізацією, якщо це не перший візит."""
    if not profile:
        return (
            "💜 <b>Головне меню</b>\n\n"
            "Оберіть, що вас цікавить — кнопки внизу екрана 👇"
        )
    from datetime import date as _date
    from data import UA_MONTHS_FULL
    name = (profile.get("name") or "").split()[0] or "вас"
    parts = [f"💜 <b>Вітаємо знову, {name}!</b>\n"]
    if profile.get("last_date"):
        try:
            dt = _date.fromisoformat(profile["last_date"])
            dd = f"{dt.day} {UA_MONTHS_FULL[dt.month]}"
        except Exception:
            dd = profile["last_date"]
        svc = profile.get("last_service") or ""
        line = f"📅 Останній візит: <b>{dd}</b>"
        if svc:
            line += f" — {svc}"
        parts.append(line)
    parts.append(f"✨ Усього візитів: <b>{profile['visits']}</b>\n")
    parts.append("Оберіть дію — кнопки внизу 👇")
    return "\n".join(parts)


# ── Тех-режим ───────────────────────────────────────────
MAINTENANCE = (
    "⚠️ <b>Технічне обслуговування</b>\n\n"
    "Бот тимчасово недоступний — скоро вже будемо працювати!\n\n"
    "Для термінового запису:\n"
    "📞 +380 67 000 00 00\n\n"
    "Дякуємо за розуміння 💜"
)


# ══ МАЙСТЕР ════════════════════════════════════════════
MASTER_PASSWORD_PROMPT = (
    "🔑 <b>Вхід для майстра</b>\n\n"
    "Введіть пароль:"
)
MASTER_WRONG_PASSWORD = "❌ Невірний пароль. Спробуйте ще раз або натисніть /start"


def master_menu_text(maintenance: bool) -> str:
    status = "🔴 УВІМКНЕНО" if maintenance else "🟢 Вимкнено"
    note = ("⚠️ Зараз клієнти бачать повідомлення про технічні роботи."
            if maintenance else "Бот працює у звичайному режимі.")
    return (
        f"🔑 <b>Панель майстра</b>\n\n"
        f"Тех. режим: {status}\n"
        f"{note}\n\n"
        f"Оберіть дію — кнопки внизу 👇"
    )


# ══ МАНІКЮР ═════════════════════════════════════════════
# Опис Ірини (підпис під фото при вході в манікюр)
MANICURE_INTRO = (
    "💅 <b>Манікюр з Іриною</b>\n\n"
    "Ірина — досвідчений майстер з понад <b>8-річним стажем</b>. "
    "Сертифікований спеціаліст, який постійно вдосконалює техніку та "
    "стежить за новинками у світі нігтьового сервісу.\n\n"
    "Її роботи — це поєднання естетики, гігієни та комфорту. "
    "А головне — вона просто чудова людина, поруч з якою ви відчуєте себе як удома. 💜\n\n"
    "<b>Оберіть тип манікюру:</b>"
)
NAIL_LENGTH = "Оберіть <b>довжину нігтів</b>:"
NAIL_SHAPE  = "Оберіть <b>форму нігтів</b>:"
CHOOSE_DATE = "Оберіть <b>дату</b> запису:"
CHOOSE_TIME = "Оберіть <b>зручний час</b>:"
NO_SLOTS    = "На жаль, на цю дату немає вільних слотів. Оберіть іншу дату 👇"


def manicure_chosen_text(type_name, len_name, shape_name):
    return (
        f"✨ <b>Ваш вибір:</b>\n\n"
        f"💅 Тип: {type_name}\n"
        f"📏 Довжина: {len_name}\n"
        f"💎 Форма: {shape_name}\n\n"
        f"Тепер оберіть зручну дату 👇"
    )


def manicure_confirm_text(type_name, len_name, shape_name, date_ua, time, discount: int = 0):
    head = "📋 <b>Підтвердіть запис:</b>"
    body = (
        f"\n\n💅 {type_name} · {len_name} · {shape_name}\n"
        f"📅 {date_ua} о {time}"
    )
    if discount:
        body += f"\n🎁 Знижка <b>−{discount}%</b>"
    body += "\n\n<i>Вартість майстер уточнить при візиті.</i>"
    return head + body


def booking_confirmed(date_ua, time, service_detail, discount: int = 0):
    extra = (f"\n🎁 З вашою знижкою −{discount}%" if discount else "")
    return (
        f"✅ <b>Запис підтверджено!</b>\n\n"
        f"📅 {date_ua} о {time}\n"
        f"💅 {service_detail}"
        f"{extra}\n\n"
        f"Нагадаємо за 24 год та за 2 год до початку.\n"
        f"До зустрічі! 💜"
    )


# ══ ПЕДИКЮР ═════════════════════════════════════════════
# Опис Івана (підпис під фото при вході в педикюр)
PEDICURE_INTRO = (
    "🦶 <b>Педикюр з Іваном</b>\n\n"
    "Іван — подолог, який за короткий час зарекомендував себе як "
    "<b>один із найкращих фахівців в Україні</b>. Сертифікований майстер, "
    "що постійно розвиває свою практику й вивчає сучасні методики.\n\n"
    "Він поєднує медичний підхід зі справжньою турботою про клієнта. "
    "А характер у Івана такий, що навіть найскладніша процедура проходить легко. 💜\n\n"
    "⚠️ <b>Важливо:</b> перед записом, будь ласка, <b>зателефонуйте Івану</b> "
    "для узгодження дати — у педикюра/подології індивідуальна тривалість, "
    "її варто обговорити заздалегідь.\n\n"
    "Лише після узгодження обирайте дату нижче 👇"
)


def pedicure_confirm_text(date_ua, time, discount: int = 0):
    extra = (f"\n🎁 Знижка <b>−{discount}%</b>" if discount else "")
    return (
        f"📋 <b>Підтвердіть запис на педикюр:</b>\n\n"
        f"🦶 Педикюр\n"
        f"📅 {date_ua} о {time}"
        f"{extra}\n\n"
        f"<i>Тривалість і вартість майстер уточнить індивідуально.</i>"
    )


def pedicure_confirmed(date_ua, time, discount: int = 0):
    extra = (f"\n🎁 З вашою знижкою −{discount}%" if discount else "")
    return (
        f"✅ <b>Запис підтверджено!</b>\n\n"
        f"🦶 Педикюр\n"
        f"📅 {date_ua} о {time}"
        f"{extra}\n\n"
        f"Майстер Іван зв'яжеться з вами для уточнення деталей.\n"
        f"До зустрічі! 💜"
    )


# ══ ГЕО ═════════════════════════════════════════════════
def geo_card(address, phone, maps_link):
    return (
        f"📍 <b>Як нас знайти</b>\n\n"
        f"{address}\n\n"
        f"🕐 Працюємо щодня 07:00–20:00\n"
        f"📞 {phone}\n\n"
        f'<a href="{maps_link}">🗺 Відкрити в Google Maps</a>'
    )


# ══ ШІ ПОМІЧНИК (для клієнта) ═══════════════════════════
AI_INTRO = (
    "🤖 <b>ШІ помічник</b>\n\n"
    "Опишіть вашу ситуацію або симптоми — я надам поради і за потреби "
    "одразу передам інформацію майстру.\n\n"
    "Наприклад: <i>«болить великий палець, є набряк», «врослий ніготь», "
    "«суха шкіра п'ят»…</i>\n\n"
    "Напишіть нижче 👇"
)
AI_THINKING = "🤔 Аналізую вашу ситуацію..."


def ai_response_text(answer):
    return f"🤖 <b>ШІ помічник:</b>\n\n{answer}"


# ══ ДЗВІНОК ═════════════════════════════════════════════
CALLBACK_INTRO = (
    "📞 <b>Замовити дзвінок майстра</b>\n\n"
    "Залиште ваш номер телефону, і майстер передзвонить найближчим часом.\n\n"
    "Введіть номер (наприклад: +380671234567):"
)
CALLBACK_QUESTION = (
    "Дякуємо! ✅\n\n"
    "Якщо бажаєте — коротко опишіть ваше питання "
    "(або /skip щоб пропустити):"
)
CALLBACK_CONFIRMED = (
    "✅ <b>Заявку прийнято!</b>\n\n"
    "Майстер передзвонить вам найближчим часом 📞\n\n"
    "До зустрічі! 💜"
)
CANCELLED = "Скасовано."


# ══ КОМАНДИ / ДОПОМОГА ═════════════════════════════════
HELP_TEXT = (
    "ℹ️ <b>Beauty &amp; Shine — бот-помічник</b>\n\n"
    "Що я вмію:\n"
    "💅 Запис на манікюр\n"
    "🦶 Запис на педикюр\n"
    "🤖 ШІ-консультація по догляду\n"
    "🎁 Скидкові вікна\n"
    "📞 Дзвінок майстра\n"
    "⏰ Нагадування про візит\n\n"
    "<b>Команди:</b>\n"
    "/start — головне меню\n"
    "/ai — ШІ помічник\n"
    "/skidky — слоти зі знижкою\n"
    "/zapys — записатись\n"
    "/help — ця довідка\n\n"
    "Користуйтесь кнопками внизу екрана 👇"
)


# ══ ІСТОРІЯ ТА МЕНЕДЖМЕНТ — МАЙСТЕР ═══════════════════
MASTER_HISTORY_PICK = "📋 <b>Історія за день</b>\n\nОберіть дату:"
MASTER_WM_SERVICE   = "🗓 <b>Менеджмент вікон</b>\n\nДля якого майстра редагувати розклад?"


def master_wm_date(service: str) -> str:
    return f"🗓 <b>Менеджмент вікон · {service}</b>\n\nОберіть дату:"


def master_wm_grid(service: str, date_ua: str) -> str:
    return (
        f"🗓 <b>{service} · {date_ua}</b>\n\n"
        f"🟢 вільно   🔴 закрито   👤 запис клієнта\n\n"
        f"Натисніть на слот щоб закрити або відкрити його. "
        f"Потім — «Зберегти»."
    )


def master_wm_saved(service: str, date_ua: str, count: int) -> str:
    return (
        f"✅ <b>Збережено!</b>\n\n"
        f"{service} · {date_ua}\n"
        f"Закрито вікон: <b>{count}</b>\n\n"
        f"Клієнти бачать ці слоти як недоступні."
    )


def master_history(date_ua: str, bookings: list) -> str:
    if not bookings:
        return f"📋 <b>{date_ua}</b>\n\nЗаписів на цю дату немає."
    lines = [f"📋 <b>{date_ua}</b>\n"]
    for bk in bookings:
        icon = "💅" if bk.get("Послуга") == "Манікюр" else "🦶"
        time = bk.get("Час", "?")
        name = bk.get("Імʼя", "—")
        uname = bk.get("Username", "")
        details = bk.get("Деталі", "")
        notes = bk.get("Нотатки ІІ", "")
        lines.append(f"\n🕐 <b>{time}</b> · {name} {uname}")
        lines.append(f"   {icon} {details}")
        if notes and notes != "—":
            lines.append(f"   📝 {notes}")
    lines.append(f"\n\n<b>Разом записів: {len(bookings)}</b>")
    return "".join(lines)


# ══ СКИДКИ — МАЙСТЕР ═══════════════════════════════════
DISCOUNT_MENU = (
    "🎁 <b>Скидкові вікна</b>\n\n"
    "Знижки допомагають швидше заповнити вільні слоти.\n\n"
    "Оберіть дію:"
)
DISCOUNT_PICK_SERVICE = "🎁 <b>Нова знижка</b>\n\nДля якої послуги?"


def discount_pick_date(service):
    return f"🎁 <b>Знижка · {service}</b>\n\nОберіть дату:"


def discount_pick_time(service, date_ua):
    return f"🎁 <b>{service} · {date_ua}</b>\n\nОберіть вільний слот для знижки:"


def discount_pick_percent(service, date_ua, time):
    return f"🎁 <b>{service} · {date_ua} · {time}</b>\n\nОберіть розмір знижки:"


def discount_saved(service, date_ua, time, percent):
    return (
        f"✅ <b>Знижку опубліковано!</b>\n\n"
        f"{('💅' if service=='Манікюр' else '🦶')} {service}\n"
        f"📅 {date_ua} о {time}\n"
        f"🎁 Знижка −{percent}%\n\n"
        f"Клієнти бачать її в розділі «Скидки»."
    )


DISCOUNT_NO_SLOTS = "На цю дату немає вільних слотів. Оберіть іншу дату 👇"
DISCOUNT_LIST_EMPTY = "Активних знижок немає.\n\nДодайте першу через «➕ Додати знижку»."
DISCOUNT_LIST_HEADER = "🎁 <b>Активні знижки</b>\n\nНатисніть щоб видалити:"
DISCOUNT_DELETED = "✅ Знижку видалено."


def discount_label(d: dict) -> str:
    from datetime import date as _date
    from data import UA_MONTHS_SHORT
    dt = _date.fromisoformat(d["date"])
    icon = "💅" if d["service"] == "Манікюр" else "🦶"
    return f"{dt.day} {UA_MONTHS_SHORT[dt.month]} · {d['time']} · {icon} −{d['percent']}%"


# ══ СКИДКИ — КЛІЄНТ ════════════════════════════════════
def client_discounts_text(discounts: list) -> str:
    if not discounts:
        return (
            "🎁 <b>Скидкові вікна</b>\n\n"
            "Зараз активних знижок немає.\n"
            "Зазирніть пізніше — вони з'являються регулярно! 💜"
        )
    from datetime import date as _date
    from data import UA_MONTHS_FULL
    lines = ["🎁 <b>Вікна зі знижкою</b>\n\nЗапишіться на ці слоти й отримайте знижку:\n"]
    for d in discounts:
        dt = _date.fromisoformat(d["date"])
        icon = "💅" if d["service"] == "Манікюр" else "🦶"
        lines.append(
            f"\n{icon} <b>{dt.day} {UA_MONTHS_FULL[dt.month]}</b> о {d['time']} "
            f"— {d['service']}, знижка <b>−{d['percent']}%</b>"
        )
    lines.append("\n\nЗнижка застосується автоматично при записі 💜")
    return "".join(lines)


# ══ ШІ ПОМІЧНИК — МАЙСТЕР ══════════════════════════════
MASTER_AI_INTRO = (
    "🤖 <b>ШІ по боту</b>\n\n"
    "Запитайте що завгодно про роботу бота — як закрити день, "
    "додати знижку, що бачить клієнт тощо.\n\n"
    "Напишіть питання нижче 👇"
)
MASTER_AI_THINKING = "🤔 Думаю..."


def master_ai_answer(answer: str) -> str:
    return f"🤖 {answer}"


# ══ НАГАДУВАННЯ ════════════════════════════════════════
def reminder_text(bk: dict, kind: str) -> str:
    from datetime import date as _date
    from data import UA_MONTHS_FULL
    icon = "💅" if bk["service"] == "Манікюр" else "🦶"
    detail = bk.get("details") or bk["service"]
    try:
        dt = _date.fromisoformat(bk["date"])
        date_ua = f"{dt.day} {UA_MONTHS_FULL[dt.month]}"
    except Exception:
        date_ua = bk["date"]
    head = ("Нагадуємо про ваш запис 💜" if kind == "24"
            else "⏰ За 2 години — ваш запис!")
    return (
        f"⏰ <b>Нагадування</b>\n\n"
        f"{head}\n\n"
        f"{icon} {detail}\n"
        f"📅 {date_ua} о {bk['time']}\n\n"
        f"Підтвердіть, будь ласка, що будете 👇"
    )


REMINDER_OK = "Дякуємо, що підтвердили! Чекаємо на вас 💜"

RESCHEDULE_SOFT = (
    "🔄 <b>Запит на перенесення прийнято</b>\n\n"
    "Майстер зателефонує вам найближчим часом, щоб підібрати нову зручну дату.\n\n"
    "До зв'язку! 💜"
)


def reschedule_penalty_warn(booking: dict) -> str:
    return (
        "⚠️ <b>Перенесення менш ніж за 2 години</b>\n\n"
        "На жаль, за такий короткий час майстер уже не встигне "
        "запропонувати це вікно іншому клієнту.\n\n"
        "<b>Умова перенесення:</b> наступний візит — звичайна вартість + 50% "
        "від вартості цього візиту (майстер уточнить суму).\n\n"
        "Майстер зателефонує для узгодження нової дати.\n\n"
        "Підтверджуєте перенесення на цих умовах?"
    )


RESCHEDULE_PENALTY_DONE = (
    "🔄 <b>Перенесення прийнято</b>\n\n"
    "Майстер зателефонує вам найближчим часом для вибору нової дати.\n\n"
    "Дякуємо за розуміння 💜"
)
RESCHEDULE_CANCELLED = "Добре, лишаємо запис без змін. Чекаємо на вас! 💜"
RESCHEDULE_NOT_FOUND = (
    "Не вдалося знайти ваш запис. Будь ласка, зателефонуйте нам — "
    "ми все вирішимо 📞"
)
