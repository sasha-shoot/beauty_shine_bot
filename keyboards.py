from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
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
def date_picker_kb(booked_dates: set | None = None) -> InlineKeyboardMarkup:
    """Показує наступні робочі дні (Пн-Сб)."""
    booked_dates = booked_dates or set()
    b = InlineKeyboardBuilder()
    today = date.today()
    added = 0

    for delta in range(1, 45):
        d = today + timedelta(days=delta)
        if d.weekday() == 6:
            continue
        if added >= 24:
            break
        d_str = d.isoformat()
        label = f"{UA_DAYS[d.weekday()]} {d.day} {UA_MONTHS_SHORT[d.month]}"
        if d_str in booked_dates:
            b.button(text=f"✗ {label}", callback_data="noop")
        else:
            b.button(text=label, callback_data=f"date:{d_str}")
        added += 1

    b.button(text="↩ Назад", callback_data="go:menu")
    b.adjust(3)
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
    """Вибір дати для майстра. prefix — префікс callback (histdate / wmdate)."""
    b = InlineKeyboardBuilder()
    today = date.today()
    b.button(text="📅 Сьогодні", callback_data=f"{prefix}:{today.isoformat()}")
    added = 0
    for delta in range(1, 50):
        d = today + timedelta(days=delta)
        if d.weekday() == 6:
            continue
        if added >= 21:
            break
        label = f"{UA_DAYS[d.weekday()]} {d.day} {UA_MONTHS_SHORT[d.month]}"
        b.button(text=label, callback_data=f"{prefix}:{d.isoformat()}")
        added += 1
    b.button(text="↩ Назад", callback_data="master:menu")
    date_rows = [3] * (added // 3)
    if added % 3:
        date_rows.append(added % 3)
    b.adjust(1, *date_rows, 1)
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
