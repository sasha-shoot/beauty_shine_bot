from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import calendar
from datetime import date, timedelta
from data import MANICURE_TYPES, NAIL_LENGTHS, NAIL_SHAPES, TIME_SLOTS, UA_DAYS, UA_MONTHS_SHORT


# ═══════════════════════════════════════════════════════════
# ТЕКСТИ КНОПОК НИЖНЬОГО МЕНЮ (reply-клавіатура)
# ═══════════════════════════════════════════════════════════
BTN = {
    # роль
    "client":     "👤 Я клієнт",
    "master":     "🔑 Я майстер",
    # клієнт
    "manicure":   "💅 Манікюр",
    "pedicure":   "🦶 Педикюр",
    "ai":         "🤖 ШІ помічник",
    "sale":       "🎁 Скидки",
    "call":       "📞 Дзвінок майстра",
    "my_orders":  "📦 Мої замовлення",
    "my_visits":  "📅 Мої записи",
    "home":       "🏠 На початок",
    "menu":       "🏠 Меню",
    # майстер
    "m_history":  "📋 Історія за день",
    "m_windows":  "🗓 Менеджмент вікон",
    "m_sale":     "🎁 Скидкові вікна",
    "m_ai":       "🤖 ШІ по боту",
    "m_tech":     "🔧 Тех. режим",
    "m_client":   "👤 Режим клієнта",
}


# ═══════════════════════════════════════════════════════════
# REPLY-КЛАВІАТУРИ (нижнє меню — як у Westelecom)
# ═══════════════════════════════════════════════════════════
def role_reply_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text=BTN["client"])
    b.button(text=BTN["master"])
    b.adjust(2)
    return b.as_markup(resize_keyboard=True)


def client_reply_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text=BTN["manicure"])
    b.button(text=BTN["pedicure"])
    b.button(text=BTN["my_orders"])
    b.button(text=BTN["my_visits"])
    b.button(text=BTN["ai"])
    b.button(text=BTN["sale"])
    b.button(text=BTN["call"])
    b.button(text=BTN["home"])
    b.adjust(2, 2, 2, 1, 1)
    return b.as_markup(resize_keyboard=True)


def master_reply_kb() -> ReplyKeyboardMarkup:
    b = ReplyKeyboardBuilder()
    b.button(text=BTN["m_history"])
    b.button(text=BTN["m_windows"])
    b.button(text=BTN["m_sale"])
    b.button(text=BTN["m_ai"])
    b.button(text=BTN["m_tech"])
    b.button(text=BTN["m_client"])
    b.button(text=BTN["home"])
    b.adjust(2, 2, 2, 1)
    return b.as_markup(resize_keyboard=True)


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


# ═══════════════════════════════════════════════════════════
# INLINE-КЛАВІАТУРИ ДЛЯ ФЛОУ
# ═══════════════════════════════════════════════════════════

# ── Манікюр: тип → довжина → форма ────────────────────────
def manicure_types_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for t in MANICURE_TYPES:
        b.button(text=t["name"], callback_data=f"mtype:{t['id']}")
    b.adjust(2)
    return b.as_markup()


def nail_lengths_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for l in NAIL_LENGTHS:
        b.button(text=l["name"], callback_data=f"mlen:{l['id']}")
    b.adjust(1)
    return b.as_markup()


def nail_shapes_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for s in NAIL_SHAPES:
        b.button(text=s["name"], callback_data=f"mshape:{s['id']}")
    b.adjust(2)
    return b.as_markup()


# ── Педикюр: одразу до дати ───────────────────────────────
def pedicure_start_kb() -> InlineKeyboardMarkup:
    """Після фото та опису Івана — запис на консультацію (без вибору дати:
    тривалість і вартість подології індивідуальні, Іван узгоджує особисто)."""
    b = InlineKeyboardBuilder()
    b.button(text="📝 Записатись на консультацію", callback_data="ped:consult")
    b.button(text="← Меню",                        callback_data="nav:menu")
    b.adjust(1)
    return b.as_markup()


# ── Вибір дати (2 місяці) ─────────────────────────────────
def _two_months_dates() -> list:
    """Робочі дні від сьогодні до кінця наступного місяця (без неділь)."""
    today = date.today()
    if today.month == 12:
        ny, nm = today.year + 1, 1
    else:
        ny, nm = today.year, today.month + 1
    last = calendar.monthrange(ny, nm)[1]
    end = date(ny, nm, last)
    out, d = [], today
    while d <= end:
        if d.weekday() != 6:
            out.append(d)
        d += timedelta(days=1)
    return out


def date_picker_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    today = date.today()
    dates = _two_months_dates()
    has_today = bool(dates) and dates[0] == today
    if has_today:
        b.button(text="📅 Сьогодні", callback_data=f"date:{today.isoformat()}")
        rest = dates[1:]
    else:
        rest = dates
    for d in rest:
        label = f"{UA_DAYS[d.weekday()]} {d.day} {UA_MONTHS_SHORT[d.month]}"
        b.button(text=label, callback_data=f"date:{d.isoformat()}")
    n = len(rest)
    rows = [3] * (n // 3)
    if n % 3:
        rows.append(n % 3)
    if has_today:
        b.adjust(1, *rows)
    else:
        b.adjust(*rows)
    return b.as_markup()


# ── Вибір часу ────────────────────────────────────────────
def time_slots_kb(available: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for slot in TIME_SLOTS:
        if slot in available:
            b.button(text=slot, callback_data=f"time:{slot}")
        else:
            b.button(text=f"{slot} ✗", callback_data="noop")
    b.button(text="↩ Обрати іншу дату", callback_data="back:date")
    b.adjust(4)
    return b.as_markup()


# ── Підтвердження ─────────────────────────────────────────
def confirm_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Підтвердити", callback_data="confirm:yes")
    b.button(text="❌ Скасувати",   callback_data="confirm:no")
    b.adjust(2)
    return b.as_markup()


# ── Inline «назад до меню» (для гео-картки, підтверджень) ──
def back_to_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🏠 Головне меню", callback_data="go:menu")
    return b.as_markup()


# ═══════════════════════════════════════════════════════════
# МАЙСТЕР — sub-flows (inline)
# ═══════════════════════════════════════════════════════════
def master_service_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💅 Манікюр (Ірина)", callback_data="wmsvc:manicure")
    b.button(text="🦶 Педикюр (Іван)",  callback_data="wmsvc:pedicure")
    b.adjust(1)
    return b.as_markup()


def master_date_kb(prefix: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    today = date.today()
    dates = _two_months_dates()
    has_today = bool(dates) and dates[0] == today
    if has_today:
        b.button(text="📅 Сьогодні", callback_data=f"{prefix}:{today.isoformat()}")
        rest = dates[1:]
    else:
        rest = dates
    for d in rest:
        label = f"{UA_DAYS[d.weekday()]} {d.day} {UA_MONTHS_SHORT[d.month]}"
        b.button(text=label, callback_data=f"{prefix}:{d.isoformat()}")
    n = len(rest)
    rows = [3] * (n // 3)
    if n % 3:
        rows.append(n % 3)
    if has_today:
        b.adjust(1, *rows)
    else:
        b.adjust(*rows)
    return b.as_markup()


def slot_grid_kb(blocked: set, booked: set) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for t in TIME_SLOTS:
        if t in booked:
            b.button(text=f"👤 {t}", callback_data="noop")
        elif t in blocked:
            b.button(text=f"🔴 {t}", callback_data=f"wmslot:{t}")
        else:
            b.button(text=f"🟢 {t}", callback_data=f"wmslot:{t}")
    b.button(text="🚫 Закрити весь день",  callback_data="wm:closeall")
    b.button(text="✅ Відкрити весь день", callback_data="wm:openall")
    b.button(text="💾 Зберегти",  callback_data="wm:save")
    b.button(text="↩ Скасувати",  callback_data="wm:cancel")
    n = len(TIME_SLOTS)
    rows = [4] * (n // 4)
    if n % 4:
        rows.append(n % 4)
    b.adjust(*rows, 1, 1, 2)
    return b.as_markup()


# ── Скидки (для майстра) ─────────────────────────────────
def discount_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Додати знижку",  callback_data="disc:add")
    b.button(text="📋 Активні знижки", callback_data="disc:list")
    b.adjust(1)
    return b.as_markup()


def discount_service_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💅 Манікюр", callback_data="dsvc:manicure")
    b.button(text="🦶 Педикюр", callback_data="dsvc:pedicure")
    b.adjust(2)
    return b.as_markup()


def discount_time_kb(available: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for t in available:
        b.button(text=t, callback_data=f"dtime:{t}")
    n = len(available)
    rows = [4] * (n // 4)
    if n % 4:
        rows.append(n % 4)
    b.adjust(*rows)
    return b.as_markup()


def discount_percent_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in (10, 15, 20, 25, 30):
        b.button(text=f"−{p}%", callback_data=f"dpct:{p}")
    b.adjust(5)
    return b.as_markup()


def discount_list_kb(discounts: list) -> InlineKeyboardMarkup:
    import texts
    b = InlineKeyboardBuilder()
    for d in discounts:
        b.button(text=f"❌ {texts.discount_label(d)}", callback_data=f"ddel:{d['id']}")
    b.adjust(1)
    return b.as_markup()


# ═══════════════════════════════════════════════════════════
# НАГАДУВАННЯ
# ═══════════════════════════════════════════════════════════
def reminder_kb(rec_id: str, kind: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Дякую, буду",     callback_data="remok")
    b.button(text="🔄 Перенести запис", callback_data=f"remmv:{rec_id}:{kind}")
    b.adjust(1)
    return b.as_markup()


def reschedule_confirm_kb(rec_id: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Так, перенести", callback_data=f"rempen:{rec_id}")
    b.button(text="❌ Ні, залишити",   callback_data="rempencancel")
    b.adjust(1)
    return b.as_markup()


# ═══════════════════════════════════════════════════════════
# НОВИЙ UX (edit-message): вікно з inline-навігацією
# ═══════════════════════════════════════════════════════════
def home_reply_kb() -> ReplyKeyboardMarkup:
    """Єдина reply-кнопка «🏠 Меню» — страховка щоб завжди повернутись."""
    b = ReplyKeyboardBuilder()
    b.button(text=BTN["menu"])
    return b.as_markup(resize_keyboard=True, is_persistent=True)


def role_inline_kb() -> InlineKeyboardMarkup:
    """Вибір ролі inline-кнопками у вітальному банері."""
    b = InlineKeyboardBuilder()
    b.button(text=BTN["client"], callback_data="role:client")
    b.button(text=BTN["master"], callback_data="role:master")
    b.adjust(1)
    return b.as_markup()


def client_menu_inline_kb() -> InlineKeyboardMarkup:
    """Головне меню клієнта — inline у вікні."""
    b = InlineKeyboardBuilder()
    b.button(text=BTN["manicure"],  callback_data="menu:manicure")
    b.button(text=BTN["pedicure"],  callback_data="menu:pedicure")
    b.button(text=BTN["my_orders"], callback_data="menu:orders")
    b.button(text=BTN["my_visits"], callback_data="menu:visits")
    b.button(text=BTN["ai"],        callback_data="menu:ai")
    b.button(text=BTN["sale"],      callback_data="menu:sale")
    b.button(text=BTN["call"],      callback_data="menu:call")
    b.adjust(2, 2, 2, 1)
    return b.as_markup()


def screen_back_kb() -> InlineKeyboardMarkup:
    """«← Меню» для інформаційних екранів вікна."""
    b = InlineKeyboardBuilder()
    b.button(text="← Меню", callback_data="nav:menu")
    return b.as_markup()


def ai_exit_kb() -> InlineKeyboardMarkup:
    """Кнопка завершення розмови з ШІ (під відповідями)."""
    b = InlineKeyboardBuilder()
    b.button(text="✅ Завершити розмову", callback_data="ai:exit")
    return b.as_markup()


def call_cancel_kb() -> InlineKeyboardMarkup:
    """Скасування флоу дзвінка."""
    b = InlineKeyboardBuilder()
    b.button(text="✖ Скасувати", callback_data="nav:menu")
    return b.as_markup()
