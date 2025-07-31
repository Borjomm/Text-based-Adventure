from dataclasses import dataclass

from global_state.game_consts import Scope

import globals as g

@dataclass
class EntityContainer:
    entity_id: int
    key: str
    health: int
    max_health: int
    ap: int
    max_ap: int
    attack: int
    
@dataclass
class AbilityContainer:
    ability_id: int
    ap: int
    scope: Scope
    key: int
    tooltip_key: int
    data_dict: dict
    available: bool