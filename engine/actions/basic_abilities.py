from .abstract_ability import AbstractAbility
from .ai_containers import Consideration
from global_state.game_consts import Proportionality, Scope
from engine.components.living_entity_components import StatsComponent, IsAliveComponent, InBattleComponent, LocalizationComponent
from engine.systems.battle_systems import process_attack, consume_ap
from engine.systems.wrappers import wrap_entity
from events.events import Event, StatsChangeEvent, BattleLogEvent
from events.event_containers import AbilityContainer
from .evaluators import evaluate_target_danger, evaluate_target_vulnerability
from util.decorators import register_ability

from typing import Self, List, Optional
from random import randint


from engine.world import World

@register_ability("basic_attack", False)
class BasicAttack(AbstractAbility):
    def __init__(self, id:int, arg_dict=None):
        self.id = id
        self.considerations = [
            Consideration(evaluate_target_vulnerability, 0.5, False, Proportionality.INVERSE),
            Consideration(evaluate_target_danger, 0.5, True, Proportionality.DIRECT)
        ]
        self.max_weight = 0.7
        self.ap = -1 #Give ap
        self.scope = Scope.ENEMIES
        self.key = "abilities.basic_attack"
        self.tooltip_key = "abilities.basic_attack_tooltip"
        self.data_dict = {"AP": self.ap}
    
    @classmethod
    def check_args(cls, arg_dict=None) -> bool:
        return True

    def execute(self, world: World, entity_id: int, target_id: int) -> List[Event]:
        log = []
        stats: StatsComponent = world.get_component(entity_id, StatsComponent)
        damage = randint(stats.attack-stats.attack_offset, stats.attack+stats.attack_offset)
        amount = process_attack(world, entity_id, target_id, damage)
        consume_ap(world, entity_id, self.ap, self.key)

        name_a: LocalizationComponent = world.get_component(entity_id, LocalizationComponent)
        name_d: LocalizationComponent = world.get_component(target_id, LocalizationComponent)

        log.append(StatsChangeEvent([wrap_entity(world, entity_id), wrap_entity(world, target_id)]))
        
        if amount:
            log.append(BattleLogEvent(name_a.attack_key, {"DAMAGE": amount}))

            stats_d: StatsComponent = world.get_component(target_id, StatsComponent)
            log.append(BattleLogEvent("entities.health_reminder", {"NAME": lambda: name_d.get_name(), "HEALTH": stats_d.health}))
        else:
            log.append(BattleLogEvent(name_a.miss_key))

        return log

    def get_state_package(self, world: World, entity_id: int) -> AbilityContainer:
        return AbilityContainer(self.id, self.ap, self.scope, self.key, self.tooltip_key, self.data_dict, self._is_available(world, entity_id))

    def _is_available(self, world: World, entity_id: int, target_id: Optional[int] = None):
        
        check = world.has_component(entity_id, InBattleComponent, IsAliveComponent)
        check2 = True
        if target_id:
            check2 = world.has_component(target_id, InBattleComponent, IsAliveComponent)
        return check and check2

    def to_dict(self) -> dict:
        return {
            "id": self.id
        }
    
    @classmethod
    def from_dict(cls, arg_dict: dict) -> Self:
        return cls(arg_dict["id"])
    

    
    

    