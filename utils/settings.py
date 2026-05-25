"""Локальні налаштування бота (тех-режим тощо).
Зберігаються у файлі bot_settings.json поруч з ботом.
"""
import json
import os
import logging

logger = logging.getLogger(__name__)

SETTINGS_FILE = "bot_settings.json"
_DEFAULTS = {"maintenance": False}


def _load() -> dict:
    if not os.path.exists(SETTINGS_FILE):
        return dict(_DEFAULTS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return {**_DEFAULTS, **json.load(f)}
    except Exception as e:
        logger.error(f"settings load error: {e}")
        return dict(_DEFAULTS)


def _save(data: dict) -> None:
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"settings save error: {e}")


def is_maintenance() -> bool:
    return _load().get("maintenance", False)


def set_maintenance(value: bool) -> None:
    data = _load()
    data["maintenance"] = value
    _save(data)
