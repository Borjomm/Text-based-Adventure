from dataclasses import dataclass, field
from typing import Callable, Any

from global_state.game_consts import Proportionality

@dataclass(frozen=True)
class Consideration:
    func: Callable
    weight: float
    needs_normalization: bool
    proportionality: Proportionality = Proportionality.DIRECT
    kwargs: dict[str, Any] = field(default_factory=dict)