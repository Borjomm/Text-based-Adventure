from prompt_toolkit.key_binding import KeyBindings

QWERTY_CYRILLIC_MAP = {
    'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е',
    'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
    'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п',
    'h': 'р', 'j': 'о', 'k': 'л', 'l': 'д',
    'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т', 'm': 'ь',
    ';': 'ж', "'": 'э', ',': 'б', '.': 'ю', '[': 'х', ']': 'ъ', '`': 'ё'
    }
# Flip it for Cyrillic → Latin
CYRILLIC_TO_LATIN = {v: k for k, v in QWERTY_CYRILLIC_MAP.items()}

class NormalizedKeyBindings(KeyBindings):
    def add(self, *keys, **kwargs):
        norm_keys = set(keys)
        for key in keys:
            for cyr, lat in CYRILLIC_TO_LATIN.items():
                if key == lat:
                    norm_keys.add(cyr)
        def decorator(handler):
            for k in norm_keys:
                KeyBindings.add(self, k, **kwargs)(handler)  # ✅ Use class name
            return handler
        return decorator