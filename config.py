import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN:         str = os.getenv("BOT_TOKEN", "")
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

AIRTABLE_TOKEN:   str = os.getenv("AIRTABLE_TOKEN", "")
AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")

IRINA_CHAT_ID: int = int(os.getenv("IRINA_CHAT_ID", "0"))
IVAN_CHAT_ID:  int = int(os.getenv("IVAN_CHAT_ID",  "0"))

# ── Майстер ───────────────────────────────────────────────
MASTER_PASSWORD: str = os.getenv("MASTER_PASSWORD", "Sarluchanu")

# ── Локація салону ────────────────────────────────────────
# Координати взяти з Google Maps: правий клік на точці → координати
SALON_LAT:     float = float(os.getenv("SALON_LAT", "45.354524007391085"))
SALON_LNG:     float = float(os.getenv("SALON_LNG", "28.82962042698601"))
SALON_ADDRESS: str   = os.getenv("SALON_ADDRESS", "ТЦ «Дельта», 2 поверх, Ізмаїл")
SALON_PHONE:   str   = os.getenv("SALON_PHONE", "+380 67 000 00 00")
