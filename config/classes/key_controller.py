from typing import Any

import globals as g
from .abstract_config import AbstractConfig
from ..option_classes import KeyOption
from util.text_renderer import invalidate_key_cache

class KeyController(AbstractConfig):
    log_key: str
    yes_key: str
    no_key: str
    arr_up: str
    arr_down: str
    arr_left: str
    arr_right: str
    enter_key: str
    quit_key: str
    tab_key: str
    def __init__(self, path:str, option_dict: dict[str, KeyOption], banned_keybinds: set[str]):
        object.__setattr__(self, "_loading", True)
        object.__setattr__(self, "banned_keybinds", banned_keybinds)
        super().__init__(path, option_dict)
        self._loading = False

    def get_all_values(self) -> dict[str, str]:
        """Helper to get a map of all current key values."""
        return {key: getattr(self, key) for key in self.option_dict}

    def __setattr__(self, name: str, value: Any):
        """Dynamically sets, validates, and saves a config value."""
        if name in self.option_dict:
            option: KeyOption = self.option_dict[name]
            new_key = str(value).lower()

            # 1. Check if this key is supposed to be fixed
            if option.fixed:
                if not self._loading:
                    g.logger.warning(f"Attempted to change fixed keybind '{name}'. Ignoring.")
                # We don't save, just silently ignore the change.
                return

            # 2. Check if the new key is in the banned list
            if new_key in self.banned_keybinds:
                g.logger.warning(f"Key '{new_key}' is banned. Reverting '{name}'.")
                return

            # 3. Check for duplicates with other keys
            all_values = self.get_all_values()
            for key_name, existing_key in all_values.items():
                if key_name != name and existing_key == new_key:
                    g.logger.warning(f"Key '{new_key}' is already assigned to '{key_name}'. Reverting '{name}'.")
                    return
            
            # If all checks pass, set the internal attribute and save
            object.__setattr__(self, f"_{name}", new_key)
            g.logger.debug(f"KEY_CONFIG: Setting {name} as {new_key}")
            invalidate_key_cache()

        else:
            # Allow setting other, non-config attributes
            object.__setattr__(self, name, value)

