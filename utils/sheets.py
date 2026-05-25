import aiohttp
import urllib.parse
import logging
from datetime import datetime
from config import AIRTABLE_TOKEN, AIRTABLE_BASE_ID
from data import TIME_SLOTS

logger = logging.getLogger(__name__)
BASE_URL = "https://api.airtable.com/v0"


def _headers() -> dict:
    return {"Authorization": f"Bearer {AIRTABLE_TOKEN}", "Content-Type": "application/json"}


def _url(table: str, params: str = "") -> str:
    t = urllib.parse.quote(table, safe="")
    u = f"{BASE_URL}/{AIRTABLE_BASE_ID}/{t}"
    return f"{u}?{params}" if params else u


# ══ ЗАПИСИ ════════════════════════════════════════════════
async def get_booked_times(date_str: str, service: str | None = None) -> set:
    """Зайняті слоти на дату. Якщо вказано service — лише для цієї послуги."""
    formula = urllib.parse.quote(f"{{Дата}}='{date_str}'")
    url = _url("Записи", f"filterByFormula={formula}")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=_headers()) as r:
                if r.status != 200:
                    logger.error(f"get_booked_times {r.status}: {await r.text()}")
                    return set()
                data = await r.json()
                result = set()
                for rec in data.get("records", []):
                    f = rec.get("fields", {})
                    if "Час" not in f:
                        continue
                    if service and f.get("Послуга") != service:
                        continue
                    result.add(f["Час"])
                return result
    except Exception as e:
        logger.error(f"get_booked_times error: {e}")
        return set()


async def get_bookings_for_date(date_str: str) -> list:
    """Усі записи на дату (для історії майстра), відсортовані за часом."""
    formula = urllib.parse.quote(f"{{Дата}}='{date_str}'")
    url = _url("Записи", f"filterByFormula={formula}")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=_headers()) as r:
                if r.status != 200:
                    logger.error(f"get_bookings_for_date {r.status}: {await r.text()}")
                    return []
                data = await r.json()
                items = [rec.get("fields", {}) for rec in data.get("records", [])]
                items.sort(key=lambda x: x.get("Час", ""))
                return items
    except Exception as e:
        logger.error(f"get_bookings_for_date error: {e}")
        return []


async def save_booking(date, time, client_name, client_username, service,
                       details, price, duration, notes: str = "",
                       chat_id: int = 0) -> bool:
    url = _url("Записи")
    payload = {"records": [{"fields": {
        "Дата": date, "Час": time, "Імʼя": client_name,
        "Username": f"@{client_username}" if client_username else "—",
        "Послуга": service, "Деталі": details,
        "Ціна": str(price), "Тривалість": str(duration),
        "Нотатки ІІ": notes or "—",
        "ChatID": str(chat_id) if chat_id else "",
    }}]}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, headers=_headers(), json=payload) as r:
                if r.status not in (200, 201):
                    logger.error(f"save_booking {r.status}: {await r.text()}")
                    return False
                return True
    except Exception as e:
        logger.error(f"save_booking error: {e}")
        return False


# ══ ЗАБЛОКОВАНІ ВІКНА ════════════════════════════════════
async def get_blocked_for_service(date_str: str, service: str) -> dict:
    """Повертає {час: record_id} для заблокованих слотів цієї послуги.
    Блоки з порожньою «Послуга» рахуються як загальні (для всіх)."""
    formula = urllib.parse.quote(f"{{Дата}}='{date_str}'")
    url = _url("Заблоковані", f"filterByFormula={formula}")
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=_headers()) as r:
                if r.status != 200:
                    logger.error(f"get_blocked_for_service {r.status}: {await r.text()}")
                    return {}
                data = await r.json()
                result = {}
                for rec in data.get("records", []):
                    f = rec.get("fields", {})
                    if "Час" not in f:
                        continue
                    svc = f.get("Послуга", "")
                    if svc == service or svc == "":
                        result[f["Час"]] = rec["id"]
                return result
    except Exception as e:
        logger.error(f"get_blocked_for_service error: {e}")
        return {}


async def get_available_times(date_str: str, service: str) -> list:
    """Вільні слоти на дату для конкретної послуги."""
    try:
        booked  = await get_booked_times(date_str, service)
        blocked = await get_blocked_for_service(date_str, service)
        unavailable = booked | set(blocked.keys())
        return [t for t in TIME_SLOTS if t not in unavailable]
    except Exception as e:
        logger.error(f"get_available_times error: {e}")
        return list(TIME_SLOTS)


async def _add_blocked(date_str: str, time: str, service: str, reason: str = "майстер") -> bool:
    url = _url("Заблоковані")
    payload = {"records": [{"fields": {
        "Дата": date_str, "Час": time, "Послуга": service, "Причина": reason,
    }}]}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, headers=_headers(), json=payload) as r:
                if r.status not in (200, 201):
                    logger.error(f"_add_blocked {r.status}: {await r.text()}")
                    return False
                return True
    except Exception as e:
        logger.error(f"_add_blocked error: {e}")
        return False


async def _delete_blocked(record_id: str) -> bool:
    url = f"{_url('Заблоковані')}/{record_id}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.delete(url, headers=_headers()) as r:
                if r.status != 200:
                    logger.error(f"_delete_blocked {r.status}: {await r.text()}")
                    return False
                return True
    except Exception as e:
        logger.error(f"_delete_blocked error: {e}")
        return False


async def save_blocked_slots(date_str: str, service: str,
                             new_blocked: set, original: dict) -> bool:
    """Зберігає зміни блокувань: додає нові, видаляє зняті.
    new_blocked — множина часів що мають бути заблоковані.
    original — {час: record_id} поточних блокувань."""
    original_set = set(original.keys())
    to_add    = new_blocked - original_set
    to_remove = original_set - new_blocked
    ok = True
    for t in to_add:
        if not await _add_blocked(date_str, t, service):
            ok = False
    for t in to_remove:
        if not await _delete_blocked(original[t]):
            ok = False
    return ok


# ══ ДЗВІНКИ ══════════════════════════════════════════════
async def save_callback(client_name, client_username, phone,
                        question, ai_flag: bool = False) -> bool:
    url = _url("Дзвінки")
    payload = {"records": [{"fields": {
        "Імʼя": client_name,
        "Username": f"@{client_username}" if client_username else "—",
        "Телефон": phone, "Питання": question or "—",
        "ІІ-прапор": "⚠️ Так" if ai_flag else "Ні",
        "Дата заявки": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }}]}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, headers=_headers(), json=payload) as r:
                if r.status not in (200, 201):
                    logger.error(f"save_callback {r.status}: {await r.text()}")
                    return False
                return True
    except Exception as e:
        logger.error(f"save_callback error: {e}")
        return False


# ══ СКИДКИ ═══════════════════════════════════════════════
async def get_discounts() -> list:
    """Список майбутніх знижок: [{id, date, time, service, percent}]."""
    from datetime import date as _date
    url = _url("Скидки")
    today = _date.today().isoformat()
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=_headers()) as r:
                if r.status != 200:
                    logger.error(f"get_discounts {r.status}: {await r.text()}")
                    return []
                data = await r.json()
                result = []
                for rec in data.get("records", []):
                    f = rec.get("fields", {})
                    d = f.get("Дата", "")
                    if not d or d < today:
                        continue
                    result.append({
                        "id": rec["id"],
                        "date": d,
                        "time": f.get("Час", ""),
                        "service": f.get("Послуга", ""),
                        "percent": str(f.get("Знижка", "0")),
                    })
                result.sort(key=lambda x: (x["date"], x["time"]))
                return result
    except Exception as e:
        logger.error(f"get_discounts error: {e}")
        return []


async def get_discount_for_slot(date_str: str, time: str, service: str) -> int:
    """% знижки для конкретного слота, або 0."""
    for d in await get_discounts():
        if d["date"] == date_str and d["time"] == time and d["service"] == service:
            try:
                return int(d["percent"])
            except (ValueError, TypeError):
                return 0
    return 0


async def add_discount(date_str: str, time: str, service: str, percent: int) -> bool:
    url = _url("Скидки")
    payload = {"records": [{"fields": {
        "Дата": date_str, "Час": time, "Послуга": service, "Знижка": str(percent),
    }}]}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, headers=_headers(), json=payload) as r:
                if r.status not in (200, 201):
                    logger.error(f"add_discount {r.status}: {await r.text()}")
                    return False
                return True
    except Exception as e:
        logger.error(f"add_discount error: {e}")
        return False


async def delete_discount(record_id: str) -> bool:
    url = f"{_url('Скидки')}/{record_id}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.delete(url, headers=_headers()) as r:
                if r.status != 200:
                    logger.error(f"delete_discount {r.status}: {await r.text()}")
                    return False
                return True
    except Exception as e:
        logger.error(f"delete_discount error: {e}")
        return False


# ══ НАГАДУВАННЯ — ЕТАП 4Б ════════════════════════════════
async def _fetch_all(table: str) -> list:
    """Отримати всі записи таблиці з пагінацією."""
    records = []
    offset = None
    try:
        async with aiohttp.ClientSession() as s:
            while True:
                params = "pageSize=100"
                if offset:
                    params += f"&offset={offset}"
                async with s.get(_url(table, params), headers=_headers()) as r:
                    if r.status != 200:
                        logger.error(f"_fetch_all {table} {r.status}: {await r.text()}")
                        break
                    data = await r.json()
                    records.extend(data.get("records", []))
                    offset = data.get("offset")
                    if not offset:
                        break
    except Exception as e:
        logger.error(f"_fetch_all error: {e}")
    return records


def _norm_booking(rec: dict) -> dict:
    f = rec.get("fields", {})
    return {
        "id": rec["id"],
        "date": f.get("Дата", ""),
        "time": f.get("Час", ""),
        "chat_id": str(f.get("ChatID", "")).strip(),
        "name": f.get("Імʼя", "—"),
        "username": f.get("Username", ""),
        "service": f.get("Послуга", ""),
        "details": f.get("Деталі", ""),
        "price": str(f.get("Ціна", "")),
        "rem24": str(f.get("Нагад24", "")).strip().lower() == "так",
        "rem2":  str(f.get("Нагад2", "")).strip().lower() == "так",
    }


async def get_upcoming_bookings() -> list:
    """Майбутні записи (сьогодні+) для планувальника нагадувань."""
    from datetime import date as _date
    today = _date.today().isoformat()
    records = await _fetch_all("Записи")
    result = []
    for rec in records:
        b = _norm_booking(rec)
        if b["date"] and b["date"] >= today:
            result.append(b)
    return result


async def get_booking_by_id(record_id: str) -> dict | None:
    """Один запис за record_id."""
    url = f"{_url('Записи')}/{record_id}"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=_headers()) as r:
                if r.status != 200:
                    logger.error(f"get_booking_by_id {r.status}: {await r.text()}")
                    return None
                return _norm_booking(await r.json())
    except Exception as e:
        logger.error(f"get_booking_by_id error: {e}")
        return None


async def mark_reminder_sent(record_id: str, which: str) -> bool:
    """Позначити що нагадування надіслано. which = '24' або '2'."""
    field = "Нагад24" if which == "24" else "Нагад2"
    url = f"{_url('Записи')}/{record_id}"
    payload = {"fields": {field: "так"}}
    try:
        async with aiohttp.ClientSession() as s:
            async with s.patch(url, headers=_headers(), json=payload) as r:
                if r.status != 200:
                    logger.error(f"mark_reminder_sent {r.status}: {await r.text()}")
                    return False
                return True
    except Exception as e:
        logger.error(f"mark_reminder_sent error: {e}")
        return False
