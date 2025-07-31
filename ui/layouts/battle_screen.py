from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.widgets import Frame

from .abstract_screen import AbstractScreen
from .settings_screen import SettingsScreen
from ..widgets import *

import globals as g
import asyncio
from util import NormalizedKeyBindings
from global_state.game_consts import Actions, ActionTypes, Scope

from events.event_containers import EntityContainer, AbilityContainer
from events.events import PlayerActionEvent, RefreshLogEvent

class BattleScreen(AbstractScreen):
    def __init__(self, parent: AbstractScreen, heroes: list[EntityContainer], enemies: list[EntityContainer]):
        super().__init__(parent)
        self.current_hero_id = None
        self.title = TextItem(key="ui.battle_screen", height=3)
        self.separator = Window(height=1, char="─")
        self.build_stats(heroes, enemies)
        
        self.action_title = TextItem(key="ui.actions", is_selectable=False)
        self.upper_frame = Frame(HSplit([
            self.title.window,
            self.separator,
            *self.stats_menu.get_windows()
            ]),
            title=g.loc.translate("ui.battlefield"))
        self.battle_log = LogWindow("ui.battle_log", 10)
        self.tooltip = TextItem(key="ui.battle_tooltip")
        self.closed_action_menu = MenuContainer([TextItem(key="ui.enemy_turn", active = False)])
        self.action_menu = self.closed_action_menu
        self.selecting_target = False
        self.ability_id = None

    def build_stats(self, heroes: list[EntityContainer], enemies: list[EntityContainer]):
        self.heroes = [StatsItem(key="ui.hero_stats", entity=hero) for hero in heroes]
        self.enemies = [StatsItem(key="ui.enemy_stats", entity=enemy) for enemy in enemies]
        all_items = self.heroes + self.enemies
        self.entity_map = {stats_item.entity.entity_id: stats_item for stats_item in all_items}
        all_items.insert(len(self.heroes), self.separator)
        self.all_stats = all_items
        self.stats_menu = MenuContainer(all_items, is_selectable=False, refreshes_index=True)
        
        
    def open_abilities(self, abilities: list[AbilityContainer]):
        self.action_menu = MenuContainer([
            AbilityItem(key=ability.key,
                     prefix = f"{id+1}. ",
                     active = ability.available,
                     handler=lambda a=ability: self.prepare_action(a),
                     container=ability) for id, ability in enumerate(abilities)])
        self.regenerate_container()

    def close_abilities(self):
        self.action_menu = self.closed_action_menu
        self.regenerate_container()


    def _regenerate_frame(self):
        self._rebuild_stats()
        self.upper_frame = Frame(HSplit([
            self.title.window,
            self.separator,
            *self.stats_menu.get_windows()
            ]),
            title=g.loc.translate("ui.battlefield"))
        
    def _rebuild_stats(self):
        all_items = self.heroes + self.enemies
        all_items.insert(len(self.heroes), self.separator)
        self.all_stats = all_items
        self.stats_menu = MenuContainer(all_items, is_selectable=False, refreshes_index=True)

    def _get_default_keybindings(self) -> NormalizedKeyBindings:
        keys = g.config.keys
        kb = super()._get_default_keybindings()
        @kb.add(keys.arr_up)
        def _(evt):
            if self.selecting_target:
                self.stats_menu.previous()
                self.refresh_stats()
            else:
                self.action_menu.previous()
                self.action_menu.refresh_text()

        @kb.add(keys.arr_down)
        def _(evt):
            if self.selecting_target:
                self.stats_menu.next()
                self.refresh_stats()
            else:
                self.action_menu.next()
                self.action_menu.refresh_text()

        @kb.add(keys.enter_key)
        def _(evt):
            if self.selecting_target:
                item = self.stats_menu.get_current_item()
                if not item:
                    return
                if not item.active:
                    return
                hero_id = self.current_hero_id
                self.execute_targeted_action(self.ability_id, hero_id, self.stats_menu.exec())
                self.ability_id = None
                self.selecting_target = False
                self.stats_menu.selectable = False
                self.action_menu.selectable = True
            else:
                self.action_menu.exec()

        @kb.add(keys.quit_key)
        def _(evt):
            if self.selecting_target:
                self.ability_id = None
                self.selecting_target = False
                self.stats_menu.selectable = False
                self.action_menu.selectable = True
            else:
                g.ui.switch_screen(SettingsScreen(self))

        return kb

    def _build_container(self) -> HSplit:
        """Builds the layout container from the current state of its children."""
        self._regenerate_frame()
        return HSplit([
            self.upper_frame,
            self.battle_log.window,
            self.action_title.window,
            *self.action_menu.get_windows(),
            self.separator,
            self.tooltip.window
        ])
    
    def refresh_stats(self):
        self.stats_menu.refresh_text()

    def refresh_all(self):
        self.refresh_stats()
        self.title.refresh_text()
        self.upper_frame.title = g.loc.translate("ui.battlefield")
        self.action_title.refresh_text()
        self.action_menu.refresh_text()
        self.tooltip.refresh_text()

        asyncio.create_task(self.battle_log.log(RefreshLogEvent()))

    def prepare_action(self, ability: AbilityContainer) -> None:
        for item in self.entity_map.values():
            item.active = False
        match ability.scope:
            case Scope.SELF:
                self.entity_map[self.current_hero_id].active = True
            case Scope.ALLIES:
                for item in self.heroes:
                    item.active = True
            case Scope.ENEMIES:
                for item in self.enemies:
                    item.active = True

        self.ability_id = ability.ability_id
        self.selecting_target = True
        self.action_menu.selectable = False
        self.stats_menu.selectable = True

        
    def execute_targeted_action(self, ability_id: int, entity_id: int, target_id: int) -> None:
        if entity_id is None:
            g.logger.warning(f"Entity_id is 'None'. Are you sure this is your turn?")
            return
        g.logger.debug(f"Received entity_id {target_id} with ability id {ability_id} for {entity_id}")
        g.ui.ui_to_engine_queue.put_nowait(PlayerActionEvent(ability_id, entity_id, target_id))
        pass

    def cleanup(self):
        self.battle_log.cleanup()
        g.logger.debug("BattleScreen cleanup complete.")
