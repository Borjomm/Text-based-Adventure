from typing import List, Set

from ..world import World
from ..components.living_entity_components import PendingDeathComponent, IsAliveComponent, IsPlayerComponent, StatsComponent, SpeedComponent, InBattleComponent, IsDeadComponent, IsEnemyComponent, BuffsComponent, BuffContainer
from events.events import BattleLogEvent

from global_state.game_consts import Defaults, Scope, Stats

def process_deaths(world: World) -> Set[int]:
    ids = world.get_entities_with(PendingDeathComponent)
    #Some custom logic (loot, experience)
    for id in ids:
        world.remove_component(id, IsAliveComponent)
        world.remove_component(id, PendingDeathComponent)
        world.add_component(id, IsDeadComponent())
    return ids

def clear_enemy_entities(world: World) -> None:
    entity_set = world.get_entities_with(IsDeadComponent)
    for id in entity_set:
        if not world.has_component(id, IsPlayerComponent):
            world.delete_entity(id)

def process_attack(world: World, attacker_id: int, defender_id: int, amount: int) -> int:
        
        #Buff damage amount here...
        buffs: BuffsComponent = world.get_component(attacker_id, BuffsComponent)
        buff_multiplier = 1.0
        for buff in buffs.buff_dict.values():
            if buff.buff_type == Stats.ATTACK:
                buff_multiplier += buff.buff_bonus

        final_amount = int(amount * buff_multiplier)

        damage = process_damage(world, defender_id, attacker_id, final_amount)
        return damage

def consume_ap(world: World, entity_id: int, amount: int, ability_key:str = "abilities.null"):
    stats: StatsComponent = world.get_component(entity_id, StatsComponent)
    if amount > stats.ap:
        raise ValueError(f"{ability_key} passed ap check, not enough ap")
    stats.ap = min(stats.max_ap, stats.ap-amount)


def process_damage(world: World, entity_id: int, source_id: int, amount: int) -> int:
        if amount <= 0:
            return 0
        stats: StatsComponent = world.get_component(entity_id, StatsComponent)

        #Resistance logic here...

        damage_taken = min(stats.health, amount)
        stats.health -= damage_taken
        if stats.health <= 0:
             world.add_component(entity_id, PendingDeathComponent())
        return damage_taken

def process_heal(world: World, source_id: int, target_id: int, amount: int) -> int:
        stats: StatsComponent = world.get_component(target_id, StatsComponent)

        available_to_restore = stats.max_health-stats.health
        if available_to_restore <= 0:
            return 0
        health_restored = min(available_to_restore, amount)
        stats.health += health_restored
        return health_restored

def apply_buff(world: World, source_id: int, target_id: int, ability_id: int, ability_key: str, buff_type: Stats, bonus: float, turns: int):
    buffs: BuffsComponent = world.get_component(target_id, BuffsComponent)
    buffs.buff_dict[ability_id] = BuffContainer(buff_key = ability_key, turns_left=turns, buff_type=buff_type, buff_bonus=bonus)

def subscribe_for_fight(world: World, *entity_ids: int):
    for entity_id in entity_ids:
        stats: StatsComponent = world.get_component(entity_id, StatsComponent)
        speed = stats.speed
        if speed <= 0:
            raise ValueError(f"Invalid speed {speed} for entity {entity_id}")
        action_value = Defaults.ACTION_VALUE_SCALE.value//speed
        world.add_component(entity_id, SpeedComponent(action_value, action_value))
        world.add_component(entity_id, InBattleComponent())

def start_turn(world: World) -> tuple[int, int]:
    """Determines the entity id to move.
    Returns tuple[entity id, action value] to be later fed into end_turn"""
    entities = world.get_entities_with(InBattleComponent, IsAliveComponent, SpeedComponent)
    if not entities:
        raise ValueError("Tried to start turn, no entities available")
    best_id = entities.pop()
    speed: SpeedComponent = world.get_component(best_id, SpeedComponent)
    best_action_value = speed.action_value
    
    for entity_id in entities:
        speed: SpeedComponent = world.get_component(entity_id, SpeedComponent)
        if speed.action_value < best_action_value:
            best_action_value = speed.action_value
            best_id = entity_id
    
    return best_id, best_action_value

def end_turn(world: World, entity_id: int, action_value: int) -> None:
    entities = world.get_entities_with(InBattleComponent, IsAliveComponent, SpeedComponent)
    if not entities:
        raise ValueError("Tried to end turn, no entities available")
    if entity_id in entities:
        speed: SpeedComponent = world.get_component(entity_id, SpeedComponent)
        speed.action_value = speed.base_action_value
        entities.remove(entity_id)

    for id in entities:
        speed: SpeedComponent = world.get_component(id, SpeedComponent)
        speed.action_value = max(0, speed.action_value-action_value)


def get_valid_target_set(world: World, entity_id: int, scope: Scope) -> set:
    # Determine the allegiance
    if world.has_component(entity_id, IsEnemyComponent):
        allegiance = "enemy"
    elif world.has_component(entity_id, IsPlayerComponent):
        allegiance = "player"
    else:
        raise ValueError(f"Unknown allegiance for {entity_id}")

    # Determine target components based on scope and allegiance
    if scope == Scope.SELF:
        return {entity_id}
    elif scope == Scope.ALLIES:
        target_component = IsEnemyComponent if allegiance == "enemy" else IsPlayerComponent
    elif scope == Scope.ENEMIES:
        target_component = IsPlayerComponent if allegiance == "enemy" else IsEnemyComponent
    else:
        raise ValueError(f"Unknown scope: {scope}")

    return world.get_entities_with(target_component, InBattleComponent, IsAliveComponent)

def update_buffs(world: World, entity_id: int) -> list[str]:
    """Cycles buffs, returns the list of ended buff keys to send in BattleLogEvents"""
    ended_keys: list[str] = []
    buffs: BuffsComponent = world.get_component(entity_id, BuffsComponent)

    if not buffs:
        return ended_keys
    
    expired_ids = [buff_id for buff_id, buff in buffs.buff_dict.items() if buff.turns_left <= 0]

    for buff_id in expired_ids:
        ended_keys.append(buffs.buff_dict[buff_id].buff_key)
        del buffs.buff_dict[buff_id]

    for buff in buffs.buff_dict.values():
        buff.turns_left = max(0, buff.turns_left - 1)

    return ended_keys
        
        
        

        
        
    
