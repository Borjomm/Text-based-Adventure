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
    untranslatable: bool = False
    
    def get_name(self):
        if self.untranslatable:
            return self.key
        return g.loc.translate(self.key)
    
@dataclass
class AbilityContainer:
    ability_id: int
    ap: int
    scope: Scope
    key: int
    tooltip_key: int
    data_dict: dict
    available: bool