from engine.blueprints.entity_blueprint import AbilityBlueprint
from engine.components.living_entity_components import AbilitiesComponent
from engine.world import World

from global_state.consts import BASIC_ABILITY_MAP, UNIQUE_ABILITY_MAP

#These are needed for dynamic registring
import engine.actions.basic_abilities
import engine.actions.unique_abilities


class AbilityFactory:
    def __init__(self):
        self.id = 0

        self.singleton_ability_map = {
        }

    def create_singletons(self, world: World):
        self.singleton_ability_map = {
            class_type: class_type(world.create_entity()) for class_type in BASIC_ABILITY_MAP.values()
        }

    def get_ability_list(self, data: list[dict]):
        ability_list = []
        for ability_dict in data:
            ability_str = ability_dict.get('id')
            if not ability_str:
                raise ValueError(f"Unable to get string id in dict {ability_dict}")
            if ability_str in BASIC_ABILITY_MAP:
                class_type = BASIC_ABILITY_MAP[ability_str]
                if not class_type.check_args(ability_dict):
                    raise ValueError(f"Invalid arguments for ability {ability_str}")
                ability_list.append(AbilityBlueprint(class_type, ability_dict))

            elif ability_str in UNIQUE_ABILITY_MAP:
                class_type = UNIQUE_ABILITY_MAP[ability_str]
                if not class_type.check_args(ability_dict):
                    raise ValueError(f"Invalid arguments for ability {ability_str}")
                ability_list.append(AbilityBlueprint(class_type, ability_dict))
            
            else:
                raise ValueError(f"Ability {ability_str} is not in AbilityFactory mapping data")
        
        return ability_list

    def make_abilities(self, world: World, ability_blueprint_list: list[AbilityBlueprint]):
        ability_dict = {}
        for ability_blueprint in ability_blueprint_list:
            if ability_blueprint.type in BASIC_ABILITY_MAP.values():
                ability_instance = self.singleton_ability_map[ability_blueprint.type]
                ability_id = ability_instance.id
                ability_dict[ability_id] = ability_instance
            
            elif ability_blueprint.type in UNIQUE_ABILITY_MAP.values():
                ability_id = world.create_entity()
                ability_dict[ability_id] = ability_blueprint.type(ability_id, ability_blueprint.data)
        
        return AbilitiesComponent(ability_dict)
