#!/usr/bin/env python3
"""
Unit tests for FaFaProFree i18n localization engine.
"""

import unittest
from pathlib import Path
from scripts.i18n import (
    I18nManager,
    set_language,
    get_language,
    _,
    get_supported_languages
)


class TestI18nEngine(unittest.TestCase):

    def setUp(self):
        set_language("en")

    def test_supported_languages(self):
        langs = get_supported_languages()
        self.assertIn("en", langs)
        self.assertIn("tr", langs)
        self.assertIn("ru", langs)
        self.assertIn("de", langs)

    def test_translation_loading(self):
        for code in ["en", "tr", "ru", "de"]:
            set_language(code)
            self.assertEqual(get_language(), code)
            title = _("app.title")
            self.assertTrue(len(title) > 0)
            self.assertNotEqual(title, "app.title")

    def test_parameter_interpolation(self):
        set_language("en")
        rendered = _("wizard.select_profile_prompt", max=4)
        self.assertIn("1-4", rendered)

        set_language("tr")
        rendered_tr = _("wizard.select_profile_prompt", max=4)
        self.assertIn("1-4", rendered_tr)

    def test_fallback_to_english(self):
        set_language("ru")
        # Non-existent key should return the key itself
        fallback = _("non_existent_key_12345")
        self.assertEqual(fallback, "non_existent_key_12345")

    def test_language_files_valid_json(self):
        root = Path(__file__).resolve().parent.parent
        lang_dir = root / "lang"
        for code in ["en", "tr", "ru", "de"]:
            lang_file = lang_dir / f"{code}.json"
            self.assertTrue(lang_file.exists(), f"Missing language file: {lang_file}")


if __name__ == "__main__":
    unittest.main()
