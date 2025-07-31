from prompt_toolkit import ANSI

from typing import Optional, Dict

import globals as g

COLORS = {
    "[reset]": "\033[0m",
    "[red]": "\033[31m",
    "[green]": "\033[32m",
    "[yellow]": "\033[33m",
    "[blue]": "\033[34m",
    "[bold]": "\033[1m",
    "[underline]": "\033[4m",
    }

KEY_ALIAS = {
    "c-m": "Enter",
    "c-i": "Tab",
    "c-h": "Backspace",
    "c-c": "Ctrl+C",
    "c-d": "Ctrl+D",
    "c-z": "Ctrl+Z",
    # Add more if needed
}

_cached_keys = None

def invalidate_key_cache():
    global _cached_keys
    _cached_keys = None

def get_len(raw_text, extra_offset=0):
    return parse_text(raw_text, extra_offset, get_len=True)

def parse_text(raw_text: str, extra_offset=0, get_len=False, format_template: Optional[Dict] = None, prefix=""):
    global _cached_keys
    if format_template:
        try:
            resolved = {k: v() if callable(v) else v for k, v in format_template.items()}
            raw_text = raw_text.format(**resolved)
        except ValueError as e:
            g.logger.warning(f"Error parsing {raw_text} - {e}")
    if g.config is not None:
        if _cached_keys is None:
            _cached_keys = g.config.keys.get_all_values()

        for key_tag, key_val in _cached_keys.items():
            display_val = KEY_ALIAS.get(key_val.lower(), key_val).upper()
            raw_text = raw_text.replace(f"[{key_tag}]", display_val)

    for tag, code in COLORS.items():
        raw_text = raw_text.replace(tag, code)
    if extra_offset:
        raw_text = ' '*extra_offset + raw_text + ' '*extra_offset
    if get_len:
        return len(raw_text)
    return ANSI(prefix+raw_text)