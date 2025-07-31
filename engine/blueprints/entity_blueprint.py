from dataclasses import dataclass
from global_state.game_consts import EntityType
from engine.actions.abstract_ability import AbstractAbility

@dataclass(frozen=True)
class AbilityBlueprint:
    type: AbstractAbility
    data: dict

@dataclass(frozen=True)
class EntityBlueprint:
    type: EntityType
    id: int
    name_key: str
    health: int
    ap: int
    max_ap: int
    attack: int
    speed: int
    can_attack: bool
    can_heal: bool
    abilities: list[AbilityBlueprint]