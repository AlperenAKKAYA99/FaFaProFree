#!/usr/bin/env python3
"""
FaFaProFree - Internationalization (i18n) Engine
================================================
Repository : https://github.com/user05-ioemlak/FaFaProFree
License    : MIT (Tooling)

Provides centralized multi-language localization for FaFaProFree:
  - Supported locales: en (English), tr (Türkçe), ru (Русский), de (Deutsch)
  - Hierarchical resolution: CLI flag > FAFA_LANG env > Config default > OS Locale > 'en'
  - Graceful key fallback: Active language -> English -> Raw Key string
  - Safe dot-notation lookup and dynamic parameter interpolation
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

SUPPORTED_LANGUAGES: Dict[str, str] = {
    "en": "English",
    "tr": "Türkçe",
    "ru": "Русский",
    "de": "Deutsch"
}

DEFAULT_LANGUAGE = "en"


class I18nManager:
    """Singleton manager for locale loading, fallback lookups, and formatting."""

    _instance: Optional["I18nManager"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(I18nManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, workspace_root: Optional[Path] = None):
        if getattr(self, "_initialized", False):
            return
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else Path(__file__).resolve().parent.parent
        self.lang_dir = self.workspace_root / "lang"
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.current_lang = DEFAULT_LANGUAGE
        self._load_language("en")  # Always load English as baseline fallback
        self._initialized = True

    def _load_language(self, lang_code: str) -> Dict[str, Any]:
        """Loads and caches language dictionary from lang/{lang_code}.json."""
        if lang_code in self._cache:
            return self._cache[lang_code]

        json_path = self.lang_dir / f"{lang_code}.json"
        data: Dict[str, Any] = {}
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        self._cache[lang_code] = data
        return data

    def set_language(self, lang_code: str) -> str:
        """Sets active language if valid, normalizing locale codes (e.g. tr_TR -> tr)."""
        code = lang_code.lower().split("_")[0].split("-")[0].strip()
        if code in SUPPORTED_LANGUAGES:
            self.current_lang = code
        else:
            self.current_lang = DEFAULT_LANGUAGE

        self._load_language(self.current_lang)
        return self.current_lang

    def get_language(self) -> str:
        """Returns the currently active language code."""
        return self.current_lang

    def detect_system_language(self) -> str:
        """Detects language from environment variables or system locale."""
        env_lang = os.environ.get("FAFA_LANG") or os.environ.get("LANG") or os.environ.get("LC_ALL") or ""
        code = env_lang.lower().split(".")[0].split("_")[0].split("-")[0].strip()
        if code in SUPPORTED_LANGUAGES:
            return code
        return DEFAULT_LANGUAGE

    def _lookup_path(self, data: Dict[str, Any], key_path: str) -> Optional[str]:
        """Traverses nested dict using dot notation."""
        parts = key_path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current if isinstance(current, (str, int, float)) else None

    def get(self, key: str, default: Optional[str] = None, **kwargs) -> str:
        """
        Translates a key with fallback hierarchy:
        1. Active language dictionary
        2. English baseline dictionary
        3. Provided default or key name itself
        """
        # 1. Lookup in active language
        active_dict = self._load_language(self.current_lang)
        val = self._lookup_path(active_dict, key)

        # 2. Fallback to English if missing
        if val is None and self.current_lang != "en":
            en_dict = self._load_language("en")
            val = self._lookup_path(en_dict, key)

        # 3. Final fallback
        if val is None:
            val = default if default is not None else key

        val_str = str(val)
        if kwargs:
            try:
                return val_str.format(**kwargs)
            except Exception:
                return val_str
        return val_str


# Global Singleton Instance
_i18n = I18nManager()


def _(key: str, **kwargs) -> str:
    """Shorthand translation helper."""
    return _i18n.get(key, **kwargs)


def t(key: str, **kwargs) -> str:
    """Alternative translation helper alias."""
    return _i18n.get(key, **kwargs)


def set_language(lang_code: str) -> str:
    """Sets the global language."""
    return _i18n.set_language(lang_code)


def get_language() -> str:
    """Returns the current language code."""
    return _i18n.get_language()


def get_supported_languages() -> Dict[str, str]:
    """Returns dict of supported languages {code: display_name}."""
    return dict(SUPPORTED_LANGUAGES)


def detect_system_language() -> str:
    """Detects system language."""
    return _i18n.detect_system_language()
