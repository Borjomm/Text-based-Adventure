from dataclasses import dataclass
from typing import Any, Type, Callable, Optional

@dataclass
class Option:
    default: Any
    "Abstract Container for saving configurations"

@dataclass
class ConfigOption(Option):
    """Represents the definition of a single configuration option."""
    type: Type  # The type to cast the value from the file (e.g., int, float, str)
    validator: Callable[[Any], Any] = lambda x: x # Optional validation/clamping function

@dataclass
class KeyOption(Option):
    """Represents the definition of a keybind item"""
    default: str
    fixed: bool = False
    render: Optional[str] = None