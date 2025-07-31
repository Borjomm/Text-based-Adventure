from .abstract_ability import AbstractAbility
from global_state.game_consts import Scope, Proportionality, Stats
from .evaluators import evaluate_target_danger, evaluate_target_vulnerability, check_target_buffs
from engine.systems.wrappers import wrap_entity
from .ai_containers import Consideration

from engine.components.living_entity_components import InBattleComponent, IsAliveComponent, StatsComponent, LocalizationComponent
from engine.world import World
from engine.systems.battle_systems import process_heal, apply_buff, consume_ap
from util.decorators import register_ability
from util import wrap_key

from events.events import StatsChangeEvent, BattleLogEvent

@register_ability("player_heal", True)
class PlayerHeal(AbstractAbility):
    def __init__(self, id, arg_dict):
        self.id = id
        self.scope = Scope[arg_dict["scope"].upper()]
        self.heal_value = arg_dict["value"]
        self.ap = arg_dict["ap_cost"]
        self.max_value = 1.0
        self.key = "abilities.player_heal"
        self.tooltip_key = "abilities.player_heal_tooltip"
        self.heal_key = "abilities.player_heal_message"
        self.self_heal_key = "abilities.player_self_heal_message"
        self.useless_heal_key = "abilities.player_useless_heal_message"
        self.data_dict = {"HEALTH": self.heal_value}

        self.considerations = [
            Consideration(evaluate_target_danger, 0.2, True, Proportionality.DIRECT),
            Consideration(evaluate_target_vulnerability, 0.8, False, Proportionality.INVERSE)
        ]

    @classmethod
    def check_args(cls, arg_dict):
        scope_str: str = arg_dict.get("scope", "")
        heal_value = arg_dict.get("value")
        ap_amount = arg_dict.get("ap_cost")
        
        is_scope_valid = scope_str.upper() in Scope.__members__
        is_value_valid = heal_value is not None
        is_ap_valid = isinstance(ap_amount, int)

        return is_scope_valid and is_value_valid and is_ap_valid
        

    def execute(self, world: World, entity_id: int, target_id: int):
        log = []
        stats: StatsComponent = world.get_component(entity_id, StatsComponent)
        consume_ap(world, entity_id, self.ap, self.key)
        healed = process_heal(world, entity_id, target_id, self.heal_value)
        name1: LocalizationComponent = world.get_component(entity_id, LocalizationComponent)
        name2: LocalizationComponent = world.get_component(target_id, LocalizationComponent)
        entity_containers = [wrap_entity(world, entity_id)]

        self_heal = entity_id == target_id

        if not self_heal:
            entity_containers.append(wrap_entity(world, target_id))
            

        log.append(StatsChangeEvent(entity_containers))
        if healed:
            log.append(BattleLogEvent(self.self_heal_key if self_heal else self.heal_key, data_dict={"ENTITY_NAME": wrap_key(name1.name_key), "TARGET_NAME": wrap_key(name2.name_key), "HEALTH": healed}))

            stats: StatsComponent = world.get_component(target_id, StatsComponent)
            log.append(BattleLogEvent("entities.health_reminder", {"NAME": wrap_key(name2.name_key), "HEALTH": stats.health}))
        else:
            log.append(BattleLogEvent(self.useless_heal_key, data_dict = {"ENTITY_NAME": wrap_key(name1.name_key), "TARGET_NAME": wrap_key(name2.name_key)}))

        return log

    def _is_available(self, world: World, entity_id, target_id = None):
        stats: StatsComponent = world.get_component(entity_id, StatsComponent)
        return world.has_component(entity_id, InBattleComponent, IsAliveComponent) and stats.ap >= self.ap

    def to_dict(self):
        return {
            "id": self.id,
            "scope": self.scope.name,
            "value": self.heal_value,
            "ap_cost": self.ap
        }
    
@register_ability("battle_cry", True)
class BattleCry(AbstractAbility):
        def __init__(self, id, arg_dict):
            self.id = id
            self.scope = Scope[arg_dict["scope"].upper()]
            self.bonus = arg_dict["bonus"]
            self.ap = arg_dict["ap_cost"]
            self.turn_amount = arg_dict["turns"]
            self.max_value = 1.0
            self.stat = Stats.ATTACK
            self.key = "abilities.battlecry"
            self.tooltip_key = "abilities.battlecry_tooltip"
            self.apply_key = "abilities.battlecry_message"
            self.apply_key_self = "abilities.battlecry_message_self"
            self.data_dict = {"BONUS": f"{int(self.bonus*100)}%", "AP": self.ap}

            self.considerations = [
                Consideration(evaluate_target_danger, 0.3, True, Proportionality.DIRECT),
                Consideration(evaluate_target_vulnerability, 0.2, False, Proportionality.INVERSE),
                Consideration(check_target_buffs, 0.5, False, Proportionality.DIRECT, {"ability_id": self.id})
            ]

        @classmethod
        def check_args(cls, arg_dict):
            scope_str: str = arg_dict.get("scope", "")
            bonus_value = arg_dict.get("bonus")
            ap_amount = arg_dict.get("ap_cost")
            turn_amount = arg_dict.get("turns")
            
            is_scope_valid = scope_str.upper() in Scope.__members__
            is_bonus_valid = bonus_value is not None and isinstance(bonus_value, float)
            is_ap_valid = isinstance(ap_amount, int)
            is_turns_valid = isinstance(turn_amount, int)

            return is_scope_valid and is_bonus_valid and is_ap_valid and is_turns_valid
        
        def execute(self, world: World, entity_id: int, target_id: int) -> list:
            log = []
            consume_ap(world, entity_id, self.ap, self.key)
            apply_buff(world, entity_id, target_id, self.id, self.key, Stats.ATTACK, self.bonus, self.turn_amount)

            name1: LocalizationComponent = world.get_component(entity_id, LocalizationComponent)
            name2: LocalizationComponent = world.get_component(target_id, LocalizationComponent)

            key = self.apply_key_self if entity_id == target_id else self.apply_key

            log.append(BattleLogEvent(key, {"ENTITY_NAME": wrap_key(name1.name_key), "TARGET_NAME": wrap_key(name2.name_key), "BONUS": int(self.bonus*100)}))

            return log
        
        def _is_available(self, world: World, entity_id, target_id = None) -> bool:
            stats: StatsComponent = world.get_component(entity_id, StatsComponent)
            return world.has_component(entity_id, InBattleComponent, IsAliveComponent) and stats.ap >= self.ap
        
        def to_dict(self) -> dict:
            return {"id": self.id, "scope": self.scope, "bonus": self.bonus, "ap_cost": self.ap, "turns": self.turn_amount}






