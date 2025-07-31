from __future__ import annotations

import yaml
from random import choices
from typing import List, TYPE_CHECKING, Optional

from .blueprints import EntityBlueprint
from global_state.game_consts import EntityType, PlayerClass, Defaults
from .world import World
from .ability_factory import AbilityFactory
from .components.living_entity_components import StatsComponent, LocalizationComponent, IsEnemyComponent, IsPlayerComponent, IsAliveComponent, AbilitiesComponent, BuffsComponent, PlayerDataComponent

import globals as g

class EntityFactory:
    def __init__(self, enemy_filepath: str, player_filepath: str):
        self.ability_factory = AbilityFactory()
        self._player_class_blueprints = {}
        self._enemy_blueprints = {}
        self.enemy_entities = {}
        self._weights = []
        self._make_enemy_blueprints(enemy_filepath)
        self._make_player_blueprints(player_filepath)

    def _make_enemy_blueprints(self, filepath: str) -> None:
        def make_enemy(id: int, data: dict) -> tuple[EntityBlueprint, int]:
            name_key = data.get('name')

            if not name_key:
                raise KeyError(f"Name for the enemy with id {id} has not been found")
            name_key = f"entities.{name_key}"
            g.logger.info(name_key)
            health = data.get('health')
            if not health:
                raise KeyError(f"Unable to get health for enemy {name_key}")
            
            attack = data.get('attack')
            if not attack:
                raise KeyError(f"Unable to get attack for enemy {name_key}")
            
            speed = data.get('speed', 100)
            
            probability = data.get('probability', 0)
            if not probability:
                print(f"Probability for enemy {name_key} has not been found. It will not be encountered")

            ap = data.get('start_ap', 1)
            max_ap = data.get('max_ap', 3)

            can_attack = data.get('can_attack', True)
            can_heal = data.get('can_heal', False)

            abilities = data.get('abilities')
            if abilities:
                ability_list = self.ability_factory.get_ability_list(abilities)

            return (EntityBlueprint(EntityType.ENEMY, id, name_key, health, ap, max_ap, attack, speed, can_attack, can_heal, ability_list), probability)

        with open(filepath, 'r', encoding="utf-8") as f:
            data: dict = yaml.safe_load(f)
            for id, entry in data.items():
                enemy_blueprint, probability = make_enemy(id, entry)
                self._enemy_blueprints[id] = enemy_blueprint
                self._weights.append(probability)

    def _make_player_blueprints(self, filepath: str) -> None:
        def make_player(id: int | str, data: dict) -> tuple[PlayerClass, EntityBlueprint]:
            class_str: str = data.get("class")
            if not class_str:
                raise KeyError(f"Class type not found for player blueprint id {id}")

            try:
                player_class = PlayerClass[class_str.upper()]
            except ValueError:
                raise ValueError(f"Invalid class type '{class_str}' for player blueprint id {id}")

            health = data.get("health")
            if health is None:
                raise KeyError(f"Health not found for player class {player_class}")
            
            speed= data.get("speed", 100)

            attack = data.get("attack")
            if attack is None:
                raise KeyError(f"Attack not found for player class {player_class}")

            ap = data.get("start_ap", 1)
            max_ap = data.get("max_ap", 3)

            name_key = "unloc.player_name"

            abilities = data.get('abilities')
            if abilities:
                ability_list = self.ability_factory.get_ability_list(abilities)

            # Players always heal and can attack
            return (
                player_class,
                EntityBlueprint(
                    type=EntityType.PLAYER,
                    id=id,
                    name_key=name_key,
                    health=health,
                    ap=ap,
                    max_ap=max_ap,
                    attack=attack,
                    speed=speed,
                    can_attack=True,
                    can_heal=True,
                    abilities=ability_list
                ),
            )

        with open(filepath, "r", encoding="utf-8") as f:
            data: dict = yaml.safe_load(f)
            for id, entry in data.items():
                player_class, blueprint = make_player(id, entry)
                self._player_class_blueprints[player_class] = blueprint

    def create_player(self, world: World, player_class: PlayerClass, name: str) -> int:
        blueprint = self._player_class_blueprints.get(player_class)
        if not blueprint:
            raise ValueError(f"No blueprint found for player class: {player_class}")
        return self.create_entity(world, blueprint, name)

    def create_entity(self, world: World, blueprint: EntityBlueprint, name: Optional[str] = None) -> int:
        def make_localization(name_key) -> LocalizationComponent:
            return LocalizationComponent(name_key, f"{name_key}_flair", f"{name_key}_attack", f"{name_key}_miss", f"{name_key}_heal", f"{name_key}_useless_heal")

        id = world.create_entity()
        component_list = []
        if blueprint.type == EntityType.PLAYER:
            component_list.append(IsPlayerComponent())
            component_list.append(PlayerDataComponent(name))
        elif blueprint.type == EntityType.ENEMY:
            component_list.append(IsEnemyComponent())
        component_list.append(StatsComponent(health=blueprint.health, max_health=blueprint.health, attack=blueprint.attack, attack_offset=Defaults.ATTACK_OFFSET.value, ap=blueprint.ap, max_ap=blueprint.max_ap, speed=blueprint.speed))
        
        component_list.append(make_localization(blueprint.name_key))
        component_list.append(BuffsComponent())
        component_list.append(IsAliveComponent())
        if blueprint.abilities:
            component_list.append(self.ability_factory.make_abilities(world, blueprint.abilities))
        else:
            component_list.append(AbilitiesComponent())
        
        world.add_components(
            id,
            *component_list
        )
        return id

    def generate_enemy_ids(self, world: World, amount:int, simple_enemy_first: bool = True) -> List[int]:
        if amount <= 0:
            raise ValueError("Impossible to create less than one enemy!")
        
        enemy_blueprints: List[EntityBlueprint] = list(self._enemy_blueprints.values())
        if not enemy_blueprints:
            raise ValueError("Enemy list is empty!")
        
        if simple_enemy_first:
            first_enemy_id = self.create_entity(world, self._enemy_blueprints.get(Defaults.ENEMY_ID.value))
            if first_enemy_id is None:
                raise ValueError(f"Simple enemy with ID {Defaults.ENEMY_ID.value} not found!")
            
            if amount == 1:
                return [first_enemy_id]
            
            amount -= 1
            enemy_ids = [self.create_entity(world, enemy_blueprint) for enemy_blueprint in choices(enemy_blueprints, self._weights, k=amount)]
            enemy_ids.insert(0, first_enemy_id)
            return enemy_ids
        
        return [self.create_entity(world, enemy_blueprint) for enemy_blueprint in choices(enemy_blueprints, self._weights, k=amount)]
    
