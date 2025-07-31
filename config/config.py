from .classes.main_config import MainConfig
from .classes.key_controller import KeyController

from config.options.main_config_options import MAIN_CONFIG_DICT
from config.options.key_config_options import KEY_CONFIG_DICT, BANNED_KEYBINDS
from global_state.consts import MAIN_CONFIG_PATH, KEY_CONFIG_PATH

class Config:
    def __init__(self):
        self.main = MainConfig(MAIN_CONFIG_PATH, MAIN_CONFIG_DICT)
        self.keys = KeyController(KEY_CONFIG_PATH, KEY_CONFIG_DICT, BANNED_KEYBINDS)
        self.sections = [
            self.main,
            self.keys
        ]

    def save(self):
        for config in self.sections:
            config.save_config_to_file()

    def __getattr__(self, name):
        """
        Forwards attribute requests to the appropriate config section.
        Allows for `g.config.language` instead of `g.config.main.language`.
        """
        # Check main config first
        if name in self.main.option_dict:
            return getattr(self.main, name)
        # Check keys config next
        if name in self.keys.option_dict:
            return getattr(self.keys, name)
        
        # If not found in any known section, raise the standard error.
        raise AttributeError(f"'Config' object has no attribute '{name}'")