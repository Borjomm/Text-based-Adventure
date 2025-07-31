from events.event_containers import EntityContainer
from engine.components.living_entity_components import StatsComponent, LocalizationComponent, IsPlayerComponent, AbilitiesComponent

from events.event_containers import AbilityContainer

from typing import List

from engine.world import World

def wrap_entity(world: World, entity_id: int) -> EntityContainer:
    stats: StatsComponent = world.get_component(entity_id, StatsComponent)
    localization: LocalizationComponent = world.get_component(entity_id, LocalizationComponent)
    is_player = world.get_component(entity_id, IsPlayerComponent)
    untranslatable = True if is_player else False

    return EntityContainer(entity_id = entity_id, key=localization.name_key, health=stats.health, max_health=stats.max_health, ap=stats.ap, max_ap=stats.max_ap, attack=stats.attack, untranslatable=untranslatable)

def wrap_entity_abilities(world: World, entity_id: int) -> List[AbilityContainer]:
    abilities: AbilitiesComponent = world.get_component(entity_id, AbilitiesComponent)
    data = abilities.data.values()
    return [ability.get_state_package(world, entity_id) for ability in data]