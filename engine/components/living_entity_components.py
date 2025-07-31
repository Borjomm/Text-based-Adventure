from __future__ import annotations
from dataclasses import dataclass, field

from global_state.game_consts import Stats
from engine.actions.abstract_ability import AbstractAbility

import globals as g

@dataclass
class StatsComponent:
    health: int
    max_health: int
    attack: int
    attack_offset: int
    ap: int
    max_ap: int
    speed: int

@dataclass
class BuffsComponent:
    buff_dict: dict[int, BuffContainer] = field(default_factory=dict)

@dataclass
class BuffContainer:
    buff_key: str
    turns_left: int
    buff_type: Stats
    buff_bonus: float

@dataclass
class SpeedComponent:
    base_action_value: int
    action_value: int

@dataclass
class CanAttackComponent:
    pass

class CanHealComponent:
    pass

@dataclass
class IsPlayerComponent:
    pass

@dataclass
class IsEnemyComponent:
    pass

@dataclass
class IsAliveComponent:
    pass

@dataclass
class IsDeadComponent:
    pass

@dataclass
class PendingDeathComponent:
    pass

@dataclass
class InBattleComponent:
    pass

@dataclass
class AbilitiesComponent:
    data: dict[int, AbstractAbility] = field(default_factory=dict)


@dataclass
class LocalizationComponent:
    name_key: str
    flair_key: str
    attack_key: str
    miss_key: str
    heal_key: str
    useless_heal_key: str

@dataclass
class PlayerDataComponent:
    name: str