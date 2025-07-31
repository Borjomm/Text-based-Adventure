from typing import TYPE_CHECKING

from engine.components.living_entity_components import StatsComponent, BuffsComponent
from global_state.game_consts import Proportionality

from engine.world import World

epsilon = 1e-6

def evaluate_target_danger(world: World, caster_id: int, target_id: int, proportionality: Proportionality, **kwargs) -> float:
    stats: StatsComponent = world.get_component(target_id, StatsComponent)
    weight = stats.attack * stats.speed
    return weight if proportionality == Proportionality.DIRECT else 1 / (weight + epsilon)

def evaluate_target_vulnerability(world: World, caster, target, proportionality: Proportionality, **kwargs) -> float:
    stats: StatsComponent = world.get_component(target, StatsComponent)
    weight = stats.health / stats.max_health
    return weight if proportionality == Proportionality.DIRECT else 1 - weight

def check_target_buffs(world: World, caster, target, proportionality: Proportionality, ability_id: int) -> float:
    buffs: BuffsComponent = world.get_component(target, BuffsComponent)
    if ability_id in buffs.buff_dict.keys():
        return 0
    return 1