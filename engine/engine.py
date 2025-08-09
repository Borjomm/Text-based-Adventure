import asyncio
import time
import os
import sys

import globals as g
from .entity_factory import EntityFactory
from .consts import DataPaths
from global_state.game_consts import PlayerClass
from .engine_event_parser import EngineEventParser
from .battle_resolver import BattleResolver
from .world import World
from events.events import ApplicationExitEvent

class GameEngine:
    def __init__(self, ui_to_engine_queue: asyncio.Queue, engine_to_ui_queue: asyncio.Queue):
        self.tick_count = 0
        self.closing = False
        self._running = False
        self.battle_running = False
        self.engine_to_ui_queue = engine_to_ui_queue
        self.event_parser = EngineEventParser(ui_to_engine_queue, self)
        enemy_filepath = os.path.join(DataPaths.DATA_FOLDER.value, DataPaths.ENEMIES.value)
        player_filepath = os.path.join(DataPaths.DATA_FOLDER.value, DataPaths.PLAYER_CLASSES.value)
        self.entity_factory = EntityFactory(enemy_filepath, player_filepath)

    async def tick(self):
            while not self.closing:
                if not self._running:
                    await asyncio.sleep(0.1)
                    continue

                next_tick = time.perf_counter()
                self.tick_count += 1

                next_tick += 1/g.config.main.tick_speed
                sleep_duration = max(0, next_tick - time.perf_counter())

                await asyncio.sleep(sleep_duration)
            #Logger output here, possible savegame
            self.engine_to_ui_queue.put_nowait(ApplicationExitEvent())

    def create_player(self, name, player_class: PlayerClass):
         self.player_id  = self.entity_factory.create_player(self.world, player_class, name)
         g.logger.debug(f"Player {name} has been created successfully with class {player_class.name.lower()}")
         g.loc.add_unlocalizable("player_name", name)

    def resume(self):
        self._running = True

    def pause(self):
        self._running = False

    def is_running(self):
        return self._running

    def stop(self):
        self.closing = True
        g.config.save()
        sys.exit(0)

    def initialize_world(self):
        self.world = World()
        self.entity_factory.ability_factory.create_singletons(self.world)

    def send(self, event):
        self.engine_to_ui_queue.put_nowait(event)

    def start_game(self):
        self.battle_resolver = BattleResolver(self, self.world, self.player_id, self.entity_factory)
        self.battle_task = asyncio.create_task(self.battle_resolver.run_battle(2))
        self.battle_running = True

    def stop_game(self):
        g.logger.debug("Stopping game...")
        if hasattr(self, "battle_task") and not self.battle_task.done():
            self.battle_task.cancel()
        self.battle_running = False
        self.world = None
        


