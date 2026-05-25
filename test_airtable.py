"""Діагностика підключення до Airtable.
Запуск:  python test_airtable.py
"""
import os
import json
import urllib.parse
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("AIRTABLE_TOKEN", "")
base  = os.getenv("AIRTABLE_BASE_ID", "")

print("=" * 50)
print(f"Токен:    {token[:14]}...{token[-6:] if len(token) > 20 else ''}")
print(f"Довжина:  {len(token)} символів")
print(f"Base ID:  {base}")
print("=" * 50)

if not token.startswith("pat"):
    print("\n❌ Токен має починатись з 'pat'. Перевір .env")
    raise SystemExit

if not base.startswith("app"):
    print("\n❌ Base ID має починатись з 'app'. Перевір .env")
    raise SystemExit

# Перевірка кожної таблиці
for table_name in ["Записи", "Заблоковані", "Дзвінки"]:
    t = urllib.parse.quote(table_name, safe="")
    url = f"https://api.airtable.com/v0/{base}/{t}?maxRecords=1"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        resp = urllib.request.urlopen(req)
        data = json.loads(resp.read())
        print(f"✅ Таблиця '{table_name}' — доступ працює")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"❌ Таблиця '{table_name}' — помилка {e.code}")
        print(f"   {body}")
    except Exception as e:
        print(f"❌ Таблиця '{table_name}' — {e}")

print("=" * 50)
print("Якщо всі ❌ — проблема в токені або Base ID.")
print("Якщо лише деякі ❌ — назва таблиці не співпадає.")
