import globals as g
from typing import Any

from ..option_classes import ConfigOption

from .abstract_config import AbstractConfig

# --- Step 3: Refactor the Config class to be data-driven ---
class MainConfig(AbstractConfig):
    def __init__(self, path: str, option_dict: dict[str, ConfigOption]) -> None:
        super().__init__(path, option_dict)

    def __setattr__(self, name: str, value: Any):
        """Dynamically sets and validates a config value. Call save() to save the changes to the config file"""
        if name in self.option_dict:
            option = self.option_dict[name]
            
            # Cast the value to the correct type
            try:
                typed_value = option.type(value)
            except ValueError:
                raise TypeError(f"Value for '{name}' must be of type {option.type.__name__}")

            # Validate/clamp the value
            validated_value = option.validator(typed_value)
            
            if validated_value != typed_value:
                 g.logger.info(f"Value for '{name}' was adjusted to '{validated_value}' by validator.")

            # Set the internal, private attribute
            object.__setattr__(self, f"_{name}", validated_value)
        else:
            # Allow setting other, non-config attributes
            object.__setattr__(self, name, value)