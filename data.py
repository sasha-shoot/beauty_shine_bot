# ── Манікюр: типи, довжини, форми ───────────────────────────
# Без цін і тривалості — їх задає майстер при підтвердженні
MANICURE_TYPES = [
    {"id": "gel",         "name": "Гель-лак"},
    {"id": "gel_clear",   "name": "Гель"},
    {"id": "strengthen",  "name": "Зміцнення"},
    {"id": "correction",  "name": "Корекція"},
    {"id": "extension",   "name": "Нарощування"},
    {"id": "spa",         "name": "SPA-манікюр"},
]

NAIL_LENGTHS = [
    {"id": "short",  "name": "Короткі (1–3)"},
    {"id": "medium", "name": "Середні (3–5)"},
    {"id": "long",   "name": "Довгі (6+)"},
]

NAIL_SHAPES = [
    {"id": "square",      "name": "Квадрат"},
    {"id": "soft_square", "name": "М'який квадрат"},
    {"id": "almond",      "name": "Мигдаль"},
    {"id": "stiletto",    "name": "Стилет"},
    {"id": "ballerina",   "name": "Балерина"},
]

# ── Розклад: 07:00–20:00 з кроком 30 хв ────────────────────
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


def get_by_id(lst: list, item_id: str) -> dict | None:
    return next((x for x in lst if x["id"] == item_id), None)
