import os
from abc import abstractmethod
from typing import Any

import globals as g

from ..option_classes import Option

from global_state.consts import BASE_SETTINGS_PATH

class AbstractConfig:
    def __init__(self, path: str, option_dict: dict[str, Option]) -> None:
        super().__setattr__("path", f"{BASE_SETTINGS_PATH}/{path}")
        super().__setattr__("option_dict", option_dict)
        # Initialize default values by iterating over our definitions
        for key, option in option_dict.items():
            # Use super's __setattr__ to avoid our custom setter during initialization
            super().__setattr__(f"_{key}", option.default)

        self.get_config_from_file()

    def get_config_from_file(self):
        if not os.path.exists(self.path):
            g.logger.warning("Config file not found. Creating with default values.")
            self.save_config_to_file()
            return

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip().split("#", 1)[0]  # Strip inline comments
                    if "=" not in line:
                        continue
                    
                    key, value = line.strip().split("=", 1)
                    key = key.strip().lower()
                    value = value.strip()

                    if key in self.option_dict.keys():
                        try:
                            # Use our generic setter to handle casting, validation, and saving
                            setattr(self, key, value)
                        except Exception as e:
                            g.logger.warning(f"Invalid value for '{key}': {value}. Reason: {e}. Using default.")
        except Exception as e:
            g.logger.error(f"Failed to read config file: {e}. Using default values.")

    def save_config_to_file(self):
        """Saves the current configuration by iterating over definitions."""
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                for key in self.option_dict:
                    # Get the current value of the private attribute
                    current_value = getattr(self, f"_{key}")
                    f.write(f"{key} = {current_value}\n")
        except Exception as e:
            g.logger.warning(f"Failed to save config file: {e}")

    def __getattr__(self, name: str) -> Any:
        """Dynamically gets a config value."""
        if name in self.option_dict:
            return getattr(self, f"_{name}")
        raise AttributeError(f"'Config' object has no attribute '{name}'")
    
    @abstractmethod
    def __setattr__(self, name, value):
        pass