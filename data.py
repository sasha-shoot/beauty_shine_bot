# ── Манікюр ───────────────────────────────────────────────
MANICURE_TYPES = [
    {"id": "classic",    "name": "Класичний",       "price": 300, "duration": 90},
    {"id": "gel",        "name": "Гель-лак",         "price": 550, "duration": 120},
    {"id": "gel_art",    "name": "Гель + малюнок",   "price": 700, "duration": 150},
    {"id": "strengthen", "name": "Зміцнення",        "price": 450, "duration": 100},
]

NAIL_LENGTHS = [
    {"id": "short",  "name": "Коротка", "price_add": 0,   "time_add": 0},
    {"id": "medium", "name": "Середня", "price_add": 50,  "time_add": 15},
    {"id": "long",   "name": "Довга",   "price_add": 100, "time_add": 30},
]

NAIL_SHAPES = [
    {"id": "square",   "name": "Квадратна",  "price_add": 0,   "time_add": 0},
    {"id": "round",    "name": "Кругла",     "price_add": 0,   "time_add": 0},
    {"id": "almond",   "name": "Мигдалева",  "price_add": 50,  "time_add": 15},
    {"id": "ballerina","name": "Балерина",   "price_add": 100, "time_add": 20},
]

# ── Розклад: 07:00–20:00 з кроком 30 хв ──────────────────
TIME_SLOTS = []
for _h in range(7, 21):
    TIME_SLOTS.append(f"{_h:02d}:00")
    if _h < 20:
        TIME_SLOTS.append(f"{_h:02d}:30")

UA_DAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
UA_MONTHS_SHORT = ["", "січ", "лют", "бер", "кві", "тра", "чер",
                   "лип", "сер", "вер", "жов", "лис", "гру"]
UA_MONTHS_FULL  = ["", "січня", "лютого", "березня", "квітня", "травня", "червня",
                   "липня", "серпня", "вересня", "жовтня", "листопада", "грудня"]

def fmt_time(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h} год {m} хв"
    elif h:
        return f"{h} год"
    return f"{m} хв"

def get_by_id(lst: list, item_id: str) -> dict | None:
    return next((x for x in lst if x["id"] == item_id), None)
