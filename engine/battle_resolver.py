from __future__ import annotations
from typing import List, TYPE_CHECKING
import asyncio

from .entity_factory import EntityFactory
from .components.living_entity_components import IsPlayerComponent, InBattleComponent, LocalizationComponent, IsAliveComponent, StatsComponent, IsEnemyComponent, AbilitiesComponent
from events.events import StartBattleEvent, StartPlayerTurnEvent, EndPlayerTurnEvent, BattleLogEvent, EntityDeathEvent, PlayerActionEvent, StatsChangeEvent, Event
from global_state.game_consts import BattleResult
if TYPE_CHECKING:
    from .engine import GameEngine

from engine.world import World
from .systems.battle_systems import process_deaths, clear_enemy_entities, subscribe_for_fight, start_turn, end_turn, get_valid_target_set, update_buffs
from .systems.wrappers import wrap_entity, wrap_entity_abilities

import globals as g

class BattleResolver:
    def __init__(self, engine: GameEngine, world: World, player_id: int, entity_factory : EntityFactory):
        self.engine = engine
        self.world = world
        self.entity_factory = entity_factory
        self.player_id = player_id
        self.player_input_attempts = 0
        self.is_player_turn = False
        self.log = []

    

    async def run_battle(self, enemy_number: int):
        try:
            #Preparing
            enemy_ids = self.entity_factory.generate_enemy_ids(self.world, enemy_number)
            subscribe_for_fight(self.world, self.player_id, *enemy_ids)


            self.engine.send(StartBattleEvent(
                heroes = [wrap_entity(self.world, self.player_id)], 
                enemies = [wrap_entity(self.world, enemy) for enemy in enemy_ids]
                ))
            await asyncio.sleep(0.2)

            #Sending flair for all enemies
            for enemy_id in enemy_ids:
                component: LocalizationComponent = self.world.get_component(enemy_id, LocalizationComponent)
                flair = component.flair_key
                self.engine.send(BattleLogEvent(flair))

            #Battle loop
            while self.world.get_entities_with(IsAliveComponent, InBattleComponent, IsEnemyComponent) and self.world.get_component(self.player_id, IsAliveComponent):
                #Log gets sent in the end of each loop
                entity_id, action_value = start_turn(self.world)
                buff_keys = update_buffs(self.world, entity_id)
                name_component: LocalizationComponent = self.world.get_component(entity_id, LocalizationComponent)
                if buff_keys:
                    for key in buff_keys:
                        self.engine.send(BattleLogEvent("abilities.buff_end", {"BUFF": lambda: g.loc.translate(key), "ENTITY_NAME": lambda: name_component.get_name()}))
                
                #Player turn gets async treatment, we wait for it to finish
                if self.world.get_component(entity_id, IsPlayerComponent):
                    self.is_player_turn = True
                    self.engine.send(StartPlayerTurnEvent(entity_id, wrap_entity_abilities(self.world, entity_id)))
                    while self.is_player_turn:
                        await asyncio.sleep(0.05)
                    self.engine.send(EndPlayerTurnEvent())

                #Attack player, maybe we'll get more logic in later
                else:
                    await self.make_turn(entity_id)

                #Death processing
                dead_ids = process_deaths(self.world)
                for id in dead_ids:
                    
                    name: LocalizationComponent = self.world.get_component(id, LocalizationComponent)
                    self.log.append(EntityDeathEvent(id))
                    self.log.append(BattleLogEvent("entities.dead_reminder", {"NAME": lambda: name.get_name()}))

                end_turn(self.world, entity_id, action_value)

                #Sending logs
                await self.send_events(self.log)
                self.log = []

                await asyncio.sleep(1)
        except asyncio.CancelledError:
            g.logger.info("Battle coroutine was cancelled")
            clear_enemy_entities(self.world)

        #Finalizing the battle
        clear_enemy_entities(self.world)
        if self.world.get_component(self.player_id, IsAliveComponent):
            return BattleResult.VICTORY
        else:
            return BattleResult.DEFEAT

    async def make_turn(self, entity_id):
        if not self.world.has_component(entity_id, IsAliveComponent):
            return
        if self.world.has_component(entity_id, IsPlayerComponent):
            return
        abilities: AbilitiesComponent = self.world.get_component(entity_id, AbilitiesComponent)
        data = abilities.data
        if not data:
            return
        
        weighted_list = []
        for ability in data.values():
            scope = ability.scope
            targets = get_valid_target_set(self.world, entity_id, scope)
            result = ability.evaluate(self.world, entity_id, targets)
            weighted_list.append((ability, *result))
        sorted_list = sorted(weighted_list, key=lambda x: x[2], reverse=True)
        
        for ability, target_id, _ in sorted_list:
            if target_id is not None:
                self.log += ability.execute(self.world, entity_id, target_id)
                return

        
    async def execute_player_action(self, action: PlayerActionEvent):
        if not self.is_player_turn:
            g.logger.warning("Tried to execute player action outside player's turn!")
            return
        #Player action gets executed
        ability_id = action.ability_id
        entity_id = action.entity_id
        target_id = action.target_id

        ability_component: AbilitiesComponent = self.world.get_component(entity_id, AbilitiesComponent)

        ability = ability_component.data.get(ability_id)
        if not ability:
            g.logger.warning(f"Player submitted ability with id {ability_id} for entity {entity_id}, but it doesn't exist for that entity. ")
            self.player_input_attempts += 1
            if self.player_input_attempts >= 3:
                self.is_player_turn = False
                self.player_input_attempts = 0
            return
        log = ability.execute(self.world, entity_id, target_id)
        self.log += log
        self.is_player_turn = False
    
    async def send_events(self, event_list: List[Event], delay: float = 0.02):
        for entry in event_list:
            g.logger.debug(f"Sending entry {entry}")
            self.engine.send(entry)
            await asyncio.sleep(delay)
        
        


        