import os
import yaml
from typing import Dict

import globals as g

from global_state.consts import LANGUAGES, DEFAULT_LANG, ALWAYS_LOADED

class LocalizationManager:
    def __init__(self, locale_dir: str = "locales", lang: str = DEFAULT_LANG):
        self.locale_dir = locale_dir
        valid_lang = lang in LANGUAGES
        self.current_lang = lang if valid_lang else DEFAULT_LANG
        self._cache: Dict[str, Dict[str, str]] = {}
        self._unloc = {}

        # Preload always-needed categories like UI
        self._always_loaded = ALWAYS_LOADED
        for cat in self._always_loaded:
            self._load_file(cat)

    def set_language(self, lang: str):
        if self.current_lang == lang:
            return
        self.current_lang = lang
        self._cache.clear()
        for cat in self._always_loaded:
            self._load_file(cat)
        g.config.main.language = lang
        g.ui.current_screen.refresh_all()

    def _load_file(self, category: str):
        path = os.path.join(self.locale_dir, self.current_lang, f"{category}.yaml")
        if not os.path.exists(path):
            g.logger.warning(f"Localization file not found: {path}, generating stub.")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                yaml.safe_dump({}, f, indent=4)
        g.logger.debug(f"Loading localization file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
            if not isinstance(loaded, dict):
                loaded = {}
            self._cache[category] = loaded

    def add_unlocalizable(self, key: str, value):
        self._unloc[key] = value
        
    def translate(self, key: str) -> str:
        if '.' not in key:
            raise ValueError(f"Localization key must be in format 'category.key', recieved {key}")
        category, inner_key = key.split('.', 1)
        if category == "unloc":
            return self._unloc.get(inner_key, f"[Missing_unloc:{key}]")
        if category not in self._cache:
            self._load_file(category)
        return self._cache[category].get(inner_key, f"[Missing:{key}]")
