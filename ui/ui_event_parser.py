from __future__ import annotations
from typing import TYPE_CHECKING

from events.events import StartBattleEvent, StatsChangeEvent, BattleLogEvent, StartPlayerTurnEvent, EndPlayerTurnEvent, EntityDeathEvent
from .layouts.battle_screen import BattleScreen
from events.event_containers import EntityContainer

from .widgets.stats_item import StatsItem

import globals as g

import asyncio
if TYPE_CHECKING:
    from .ui_controller import UiController

class UiEventParser:
    def __init__(self, engine_to_ui_queue: asyncio.Queue, controller: UiController):
        self.engine_to_ui_queue = engine_to_ui_queue
        self.controller = controller

    async def process_events(self):
        while not self.controller.closing:
            event = await self.engine_to_ui_queue.get()
            match event:
                case StartBattleEvent():
                    self.start_battle(event)
                case StatsChangeEvent():
                    self.replace_entities(event)
                case StartPlayerTurnEvent():
                    self.start_player_turn(event)
                case EndPlayerTurnEvent():
                    self.end_player_turn()
                case BattleLogEvent():
                    self.add_battle_log(event)
                case EntityDeathEvent():
                    self.handle_death(event.entity_id)
                case _:
                    g.logger.warning(f"Unknown event: {event}")

            


    def start_battle(self, event:StartBattleEvent):
        screen = BattleScreen(g.ui.current_screen, event.heroes, event.enemies)
        g.ui.battle_screen = screen
        g.ui.switch_screen(screen)

    def replace_entities(self, event:StatsChangeEvent):
        screen = g.ui.battle_screen
        if not isinstance(screen, BattleScreen):
            g.logger.warning("Tried to give entity stats while not on battle screen, skipping")
            return
        for entity in event.entities:
            g.logger.debug(f"Changing stats for {entity} with entity id {entity.entity_id}")
            stat_item: StatsItem = screen.entity_map[entity.entity_id]
            stat_item.entity = entity
        screen.refresh_stats()

    def start_player_turn(self, event:StartPlayerTurnEvent):
        screen = g.ui.battle_screen
        if not isinstance(screen, BattleScreen):
            g.logger.warning("Tried to give entity stats while not on battle screen, skipping")
            return
        screen.current_hero_id = event.entity_id
        screen.open_abilities(event.abilities)

    def end_player_turn(self):
        screen = g.ui.battle_screen
        if not isinstance(screen, BattleScreen):
            g.logger.warning("Tried to give entity stats while not on battle screen, skipping")
            return
        screen.current_hero_id = None
        screen.close_abilities()

    def add_battle_log(self, event: BattleLogEvent):
        screen = g.ui.battle_screen
        if not isinstance(screen, BattleScreen):
            g.logger.warning("Tried to append battle log while not on battle screen, skipping")
            return
        asyncio.create_task(screen.battle_log.log(event))


    def handle_death(self, entity_id):
        screen = g.ui.battle_screen
        if not isinstance(screen, BattleScreen):
            g.logger.warning("Tried to process death event while not on battle screen, skipping")
            return
        stat_item = screen.entity_map.get(entity_id)
        if not stat_item:
            return
        if stat_item in screen.heroes:
            screen.heroes.remove(stat_item)
        elif stat_item in screen.enemies:
            screen.enemies.remove(stat_item)
        del screen.entity_map[entity_id]
        
        screen.regenerate_container()

            


