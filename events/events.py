from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, List, Any, TYPE_CHECKING


if TYPE_CHECKING:
    from global_state.game_consts import PlayerClass
    from .event_containers import EntityContainer, AbilityContainer

@dataclass
class Event:
    pass

@dataclass
class GameStartEvent(Event):
    player_name: str
    player_class: PlayerClass
    save_state: Optional[Dict] = None

@dataclass
class StartBattleEvent(Event):
    heroes: List[EntityContainer]
    enemies: List[EntityContainer]

@dataclass
class PlayerActionEvent(Event):
    ability_id: int
    entity_id: int
    target_id: Optional[int] = None

@dataclass
class BattleLogEvent(Event):
    message_key: str
    data_dict: Optional[Dict[str,Any]] = None

@dataclass
class UiUpdateEvent(Event):
    ability_key: str
    tooltip_key: str
    data_dict: Optional[Dict[str,Any]] = None

@dataclass
class RefreshLogEvent(Event):
    pass

@dataclass
class EntityDeathEvent(Event):
    entity_id: int

@dataclass
class StatsChangeEvent(Event):
    entities: List[EntityContainer]

@dataclass
class StartPlayerTurnEvent(Event):
    entity_id: int
    abilities: List[AbilityContainer]

@dataclass
class EndPlayerTurnEvent(Event):
    pass

@dataclass
class GameStopEvent(Event):
    pass
    