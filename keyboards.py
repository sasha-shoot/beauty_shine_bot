from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import calendar
from datetime import date, timedelta
from data import MANICURE_TYPES, NAIL_LENGTHS, NAIL_SHAPES, TIME_SLOTS, UA_DAYS, UA_MONTHS_SHORT


# ── Вибір ролі ────────────────────────────────────────────
def role_select_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="👤 Я клієнт",  callback_data="role:client")
    b.button(text="🔑 Я майстер", callback_data="role:master")
    b.adjust(1)
    return b.as_markup()


# ── Панель майстра ────────────────────────────────────────
def master_menu_kb(maintenance: bool) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if maintenance:
        b.button(text="✅ Вимкнути тех. режим", callback_data="master:maintenance")
    else:
        b.button(text="🔧 Увімкнути тех. режим", callback_data="master:maintenance")
    b.button(text="📋 Історія за день", callback_data="master:history")
    b.button(text="🗓 Менеджмент вікон", callback_data="master:windows")
    b.button(text="🎁 Скидкові вікна", callback_data="master:discounts")
    b.button(text="🤖 ІІ помічник по боту", callback_data="master:ai")
    b.button(text="👤 Перейти в режим клієнта", callback_data="role:client")
    b.button(text="↩ На початок", callback_data="go:start")
    b.adjust(1)
    return b.as_markup()


# ── Головне меню клієнта ─────────────────────────────────
def main_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💅 Манікюр",          callback_data="svc:manicure")
    b.button(text="🦶 Педикюр",          callback_data="svc:pedicure")
    b.button(text="🤖 ІІ помічник",      callback_data="svc:ai")
    b.button(text="📞 Замовити дзвінок", callback_data="svc:callback")
    b.button(text="🎁 Скидкові вікна",   callback_data="svc:discounts")
    b.adjust(2, 1, 1, 1)
    return b.as_markup()


# ── Манікюр ───────────────────────────────────────────────
def manicure_types_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for t in MANICURE_TYPES:
        b.button(text=t["name"], callback_data=f"mtype:{t['id']}")
    b.button(text="↩ Назад", callback_data="go:menu")
    b.adjust(2, 2, 1)
    return b.as_markup()

def nail_lengths_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for l in NAIL_LENGTHS:
        label = l["name"] + (f" (+{l['price_add']} грн)" if l["price_add"] else "")
        b.button(text=label, callback_data=f"mlen:{l['id']}")
    b.adjust(3)
    return b.as_markup()

def nail_shapes_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for s in NAIL_SHAPES:
        label = s["name"] + (f" (+{s['price_add']} грн)" if s["price_add"] else "")
        b.button(text=label, callback_data=f"mshape:{s['id']}")
    b.adjust(2)
    return b.as_markup()


# ── Вибір дати ────────────────────────────────────────────

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
        if d.weekday() != 6:  # пропускаємо неділі
            out.append(d)
        d += timedelta(days=1)
    return out


def date_picker_kb() -> InlineKeyboardMarkup:
    """Дати від сьогодні до кінця наступного місяця (без неділь)."""
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
    b.button(text="↩ Назад", callback_data="go:menu")
    n = len(rest)
    rows = [3] * (n // 3)
    if n % 3:
        rows.append(n % 3)
    if has_today:
        b.adjust(1, *rows, 1)
    else:
        b.adjust(*rows, 1)
    return b.as_markup()


# ── Вибір часу ────────────────────────────────────────────
def time_slots_kb(available: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for slot in TIME_SLOTS:
        if slot in available:
            b.button(text=slot,        callback_data=f"time:{slot}")
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


# ── Педикюр ───────────────────────────────────────────────
def pedicure_options_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📅 Обрати дату",     callback_data="ped:date")
    b.button(text="📞 Замовити дзвінок", callback_data="ped:call")
    b.button(text="↩ Назад",            callback_data="go:menu")
    b.adjust(1)
    return b.as_markup()


# ── Після ІІ ─────────────────────────────────────────────
def ai_after_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💅 Записатись",       callback_data="svc:manicure")
    b.button(text="🦶 Педикюр",          callback_data="svc:pedicure")
    b.button(text="📞 Замовити дзвінок", callback_data="svc:callback")
    b.button(text="↩ Головне меню",      callback_data="go:menu")
    b.adjust(2, 1, 1)
    return b.as_markup()


# ── Загальне ─────────────────────────────────────────────
def back_to_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🏠 Головне меню", callback_data="go:menu")
    return b.as_markup()


# ══ МАЙСТЕР — ЕТАП 2 ═════════════════════════════════════
def master_service_kb() -> InlineKeyboardMarkup:
    """Вибір послуги для менеджменту вікон."""
    b = InlineKeyboardBuilder()
    b.button(text="💅 Манікюр (Ірина)", callback_data="wmsvc:manicure")
    b.button(text="🦶 Педикюр (Іван)",  callback_data="wmsvc:pedicure")
    b.button(text="↩ Назад", callback_data="master:menu")
    b.adjust(1)
    return b.as_markup()


def master_date_kb(prefix: str) -> InlineKeyboardMarkup:
    """Вибір дати для майстра — до кінця наступного місяця."""
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
    b.button(text="↩ Назад", callback_data="master:menu")
    n = len(rest)
    rows = [3] * (n // 3)
    if n % 3:
        rows.append(n % 3)
    if has_today:
        b.adjust(1, *rows, 1)
    else:
        b.adjust(*rows, 1)
    return b.as_markup()


def slot_grid_kb(blocked: set, booked: set) -> InlineKeyboardMarkup:
    """Сітка слотів для менеджменту вікон."""
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
    b.button(text="↩ Скасувати",  callback_data="master:menu")
    n = len(TIME_SLOTS)
    slot_rows = [4] * (n // 4)
    if n % 4:
        slot_rows.append(n % 4)
    b.adjust(*slot_rows, 1, 1, 2)
    return b.as_markup()


def back_to_master_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="↩ Панель майстра", callback_data="master:menu")
    return b.as_markup()


# ══ СКИДКИ — ЕТАП 3 ══════════════════════════════════════
def discount_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Додати знижку",  callback_data="disc:add")
    b.button(text="📋 Активні знижки", callback_data="disc:list")
    b.button(text="↩ Панель майстра",  callback_data="master:menu")
    b.adjust(1)
    return b.as_markup()

def discount_service_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💅 Манікюр", callback_data="dsvc:manicure")
    b.button(text="🦶 Педикюр", callback_data="dsvc:pedicure")
    b.button(text="↩ Назад",    callback_data="master:discounts")
    b.adjust(2, 1)
    return b.as_markup()

def discount_time_kb(available: list) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for t in available:
        b.button(text=t, callback_data=f"dtime:{t}")
    b.button(text="↩ Скасувати", callback_data="master:discounts")
    n = len(available)
    rows = [4] * (n // 4)
    if n % 4:
        rows.append(n % 4)
    b.adjust(*rows, 1)
    return b.as_markup()

def discount_percent_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for p in (10, 15, 20, 25, 30):
        b.button(text=f"−{p}%", callback_data=f"dpct:{p}")
    b.button(text="↩ Скасувати", callback_data="master:discounts")
    b.adjust(5, 1)
    return b.as_markup()

def discount_list_kb(discounts: list) -> InlineKeyboardMarkup:
    import texts
    b = InlineKeyboardBuilder()
    for d in discounts:
        b.button(text=f"❌ {texts.discount_label(d)}", callback_data=f"ddel:{d['id']}")
    b.button(text="↩ Назад", callback_data="master:discounts")
    b.adjust(1)
    return b.as_markup()

def master_ai_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="↩ Панель майстра", callback_data="master:menu")
    return b.as_markup()

def client_discounts_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💅 Записатись на манікюр", callback_data="svc:manicure")
    b.button(text="🦶 Записатись на педикюр", callback_data="svc:pedicure")
    b.button(text="↩ Головне меню", callback_data="go:menu")
    b.adjust(1)
    return b.as_markup()


# ══ НАГАДУВАННЯ — ЕТАП 4Б ════════════════════════════════
def reminder_kb(rec_id: str, kind: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Дякую, буду",      callback_data="remok")
    b.button(text="🔄 Перенести запис",  callback_data=f"remmv:{rec_id}:{kind}")
    b.adjust(1)
    return b.as_markup()

def reschedule_confirm_kb(rec_id: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="✅ Так, перенести", callback_data=f"rempen:{rec_id}")
    b.button(text="❌ Ні, залишити",   callback_data="rempencancel")
    b.adjust(1)
    return b.as_markup()
