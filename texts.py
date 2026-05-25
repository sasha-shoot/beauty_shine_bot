# ══ ВХІД / РЕЖИМИ ════════════════════════════════════════
ROLE_SELECT = (
    "Вітаємо у <b>Beauty &amp; Shine</b> 💜\n\n"
    "Студія краси та здоров'я в Ізмаїлі (ТЦ Дельта).\n\n"
    "Оберіть режим входу:"
)

# ── Головне меню клієнта ─────────────────────────────────
WELCOME = (
    "Головне меню 💜\n\n"
    "Оберіть, будь ласка, що вас цікавить:"
)

# ── Тех-режим ─────────────────────────────────────────────
MAINTENANCE = (
    "⚠️ <b>Технічні роботи</b>\n\n"
    "Бот тимчасово недоступний — проводимо оновлення.\n\n"
    "Для запису, будь ласка, зателефонуйте нам:\n"
    "📞 +380 67 000 00 00\n\n"
    "Дякуємо за розуміння! 💜"
)

# ── Майстер ───────────────────────────────────────────────
MASTER_PASSWORD_PROMPT = (
    "🔑 <b>Вхід для майстра</b>\n\n"
    "Введіть пароль:"
)
MASTER_WRONG_PASSWORD = (
    "❌ Невірний пароль.\n\n"
    "Спробуйте ще раз або натисніть /start"
)

def master_menu_text(maintenance: bool) -> str:
    status = "🔴 УВІМКНЕНО" if maintenance else "🟢 Вимкнено"
    note = ("⚠️ Зараз клієнти бачать повідомлення про технічні роботи."
            if maintenance else "Бот працює у звичайному режимі.")
    return (
        f"🔑 <b>Панель майстра</b>\n\n"
        f"Тех. режим: {status}\n"
        f"{note}\n\n"
        f"Оберіть дію:"
    )

# ── Манікюр ───────────────────────────────────────────────
MANICURE_TYPE   = "Оберіть <b>тип манікюру</b>:"
NAIL_LENGTH     = "Оберіть <b>довжину нігтів</b>:"
NAIL_SHAPE      = "Оберіть <b>форму нігтів</b>:"
CHOOSE_DATE     = "Оберіть <b>дату</b> запису:"
CHOOSE_TIME     = "Оберіть <b>зручний час</b>:"
NO_SLOTS        = "На жаль, на цю дату немає вільних слотів. Оберіть іншу дату 👇"

def manicure_summary(type_name, len_name, shape_name, duration_str, price, date_ua):
    return (
        f"✨ <b>Ваш вибір:</b>\n\n"
        f"💅 Тип: {type_name}\n"
        f"📏 Довжина: {len_name}\n"
        f"💎 Форма: {shape_name}\n"
        f"⏱ Тривалість: ~{duration_str}\n"
        f"💰 Вартість: <b>{price} грн</b>\n\n"
        f"Тепер оберіть зручну дату 👇"
    )

def time_choice_text(date_ua, duration_str):
    return f"📅 <b>{date_ua}</b>\n\nОберіть зручний час (тривалість ~{duration_str}):"

def manicure_confirm_text(type_name, len_name, shape_name, date_ua, time, duration_str, price):
    return (
        f"📋 <b>Підтвердіть запис:</b>\n\n"
        f"💅 {type_name} · {len_name} · {shape_name}\n"
        f"📅 {date_ua} о {time}\n"
        f"⏱ ~{duration_str}\n"
        f"💰 {price} грн"
    )

def booking_confirmed(date_ua, time, service_detail, price):
    return (
        f"✅ <b>Запис підтверджено!</b>\n\n"
        f"📅 {date_ua} о {time}\n"
        f"💅 {service_detail}\n"
        f"💰 {price} грн\n\n"
        f"Нагадаємо за 24 год та за 2 год до початку.\n"
        f"До зустрічі! 💜"
    )

# ── Педикюр ───────────────────────────────────────────────
PEDICURE_INTRO = (
    "🦶 <b>Педикюр</b>\n\n"
    "Майстер Іван Петрович індивідуально скорегує тривалість під вашу ситуацію.\n\n"
    "<b>Орієнтовно:</b> 1–2 год\n\n"
    "Що бажаєте зробити?"
)

def pedicure_confirm_text(date_ua, time):
    return (
        f"📋 <b>Підтвердіть запис на педикюр:</b>\n\n"
        f"🦶 Педикюр (медичний + косметичний)\n"
        f"📅 {date_ua} о {time}\n"
        f"⏱ Тривалість уточнюється індивідуально\n"
        f"💰 Вартість оголосить майстер"
    )

def pedicure_confirmed(date_ua, time):
    return (
        f"✅ <b>Запис підтверджено!</b>\n\n"
        f"🦶 Педикюр\n"
        f"📅 {date_ua} о {time}\n\n"
        f"Майстер Іван Петрович зв'яжеться з вами для уточнення деталей.\n"
        f"До зустрічі! 💜"
    )

# ── Гео ───────────────────────────────────────────────────
def geo_card(address, phone, maps_link):
    return (
        f"📍 <b>Як нас знайти</b>\n\n"
        f"{address}\n\n"
        f"🕐 Працюємо щодня 07:00–20:00\n"
        f"📞 {phone}\n\n"
        f'<a href="{maps_link}">🗺 Відкрити в Google Maps</a>'
    )

# ── ІІ Помічник ───────────────────────────────────────────
AI_INTRO = (
    "🤖 <b>ІІ Помічник</b>\n\n"
    "Опишіть вашу ситуацію або симптоми — я надам поради та за потреби "
    "одразу передам інформацію майстру.\n\n"
    "Наприклад: <i>«болить великий палець, є набряк», «вросший ніготь», "
    "«суха шкіра п'ят»...</i>\n\n"
    "Напишіть нижче 👇"
)
AI_THINKING = "🤔 Аналізую вашу ситуацію..."

def ai_response_text(answer):
    return f"🤖 <b>ІІ Помічник:</b>\n\n{answer}\n\nЩо бажаєте зробити далі?"

# ── Дзвінок ───────────────────────────────────────────────
CALLBACK_INTRO = (
    "📞 <b>Замовити дзвінок-консультацію</b>\n\n"
    "Залиште ваш номер телефону, і майстер передзвонить найближчим часом.\n\n"
    "Введіть номер (наприклад: +380671234567):"
)
CALLBACK_QUESTION = (
    "Дякуємо! ✅\n\n"
    "Якщо бажаєте — коротко опишіть ваше питання або ситуацію "
    "(або надішліть /skip щоб пропустити):"
)
CALLBACK_CONFIRMED = (
    "✅ <b>Заявку прийнято!</b>\n\n"
    "Майстер передзвонить вам найближчим часом 📞\n\n"
    "До зустрічі! 💜"
)

CANCELLED = "Скасовано. Повертаємось до головного меню."


# ══ МАЙСТЕР — ЕТАП 2 ═════════════════════════════════════
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
    total = 0
    for bk in bookings:
        icon = "💅" if bk.get("Послуга") == "Манікюр" else "🦶"
        time = bk.get("Час", "?")
        name = bk.get("Імʼя", "—")
        uname = bk.get("Username", "")
        details = bk.get("Деталі", "")
        price = bk.get("Ціна", "")
        lines.append(f"\n🕐 <b>{time}</b> · {name} {uname}")
        row = f"   {icon} {details}"
        if price and price not in ("уточнюється", "—", ""):
            row += f" · {price} грн"
            try:
                total += int(price)
            except ValueError:
                pass
        lines.append(row)
    lines.append(f"\n\n<b>Разом записів: {len(bookings)}</b>")
    if total:
        lines.append(f"\n💰 Сума (манікюр): {total} грн")
    return "".join(lines)


# ══ СКИДКИ — МАЙСТЕР ═════════════════════════════════════
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
        f"Клієнти бачать її в розділі «Скидкові вікна»."
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

# ══ СКИДКИ — КЛІЄНТ ══════════════════════════════════════
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
    lines.append("\n\nЗнижка застосується автоматично при записі на цей слот 💜")
    return "".join(lines)

# ══ ІІ ПОМІЧНИК ПО БОТУ — МАЙСТЕР ════════════════════════
MASTER_AI_INTRO = (
    "🤖 <b>ІІ помічник по боту</b>\n\n"
    "Запитайте що завгодно про роботу бота — як закрити день, "
    "додати знижку, що бачить клієнт тощо.\n\n"
    "Напишіть питання нижче 👇"
)
MASTER_AI_THINKING = "🤔 Думаю..."

def master_ai_answer(answer: str) -> str:
    return f"🤖 {answer}"


# ══ НАГАДУВАННЯ — ЕТАП 4Б ════════════════════════════════
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
    price = booking.get("price", "")
    try:
        penalty = round(int(price) * 0.5)
        pen_str = f"<b>{penalty} грн</b> (50% вартості цього запису)"
    except (ValueError, TypeError):
        pen_str = "<b>+50%</b> від вартості цього візиту (майстер уточнить суму)"
    return (
        "⚠️ <b>Перенесення менш ніж за 2 години</b>\n\n"
        "На жаль, за такий короткий час майстер уже не встигне "
        "запропонувати це вікно іншому клієнту.\n\n"
        f"<b>Умова перенесення:</b> наступний візит — звичайна вартість + {pen_str}.\n\n"
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
