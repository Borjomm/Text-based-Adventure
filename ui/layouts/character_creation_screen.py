from prompt_toolkit.layout import HSplit, Window

from .abstract_screen import AbstractScreen
from ..widgets import *

import globals as g
from util import NormalizedKeyBindings
from global_state.game_consts import PlayerClass

from events.events import GameStartEvent

class CharacterCreationScreen(AbstractScreen):
    def __init__(self, parent: AbstractScreen):
        super().__init__(parent)
        class_options = [SettingItem(key=f"ui.{c.name.lower()}", option=c.name) for c in PlayerClass]
        self.title = TextItem(key="ui.create_character", height=3)
        self.separator = Window(height=1, char="─")
        self.name_selector = TextInputItem(key="ui.enter_name")
        self.class_selector = SelectionMenuItem(key="ui.select_class", screen=self, options=class_options, selected_index=0)
        
        self.menu_items = MenuContainer([
            self.name_selector,
            self.class_selector,
            None,
            MenuItem(key="ui.start_game", handler=self.start_game),
            None,
            MenuItem(key="ui.back", handler=self.exit)
        ])
        self.tooltip = TextItem(key="ui.creator_tooltip")

        self.class_map = {e.name: e for e in PlayerClass}

    def _get_default_keybindings(self) -> NormalizedKeyBindings:
        keys = g.config.keys
        kb = super()._get_default_keybindings()
        @kb.add(keys.arr_up)
        def _(evt):
            self.menu_items.previous()
            self.refresh_all()

        @kb.add(keys.arr_down)
        def _(evt):
            self.menu_items.next()
            self.refresh_all()

        @kb.add(keys.enter_key)
        def _(evt):
            self.menu_items.exec()

        return kb
    
    def start_game(self):
        name = self.name_selector.get_text()
        if not name:
            self.tooltip.set_temp_key("ui.blank_name", 1)
            return
        g.engine.resume()
        name = self.name_selector.get_text()
        player_class_str = self.class_selector.get_option()
        player_class = self.class_map[player_class_str]
        event = GameStartEvent(name, player_class)
        g.ui.ui_to_engine_queue.put_nowait(event)

    def _build_container(self) -> HSplit:
        """Builds the layout container from the current state of its children."""
        return HSplit([
            self.title.window,
            self.separator,
            *self.menu_items.get_windows(),
            self.separator,
            self.tooltip.window
        ])

    def refresh_all(self):
        self.title.refresh_text()
        self.menu_items.refresh_text()
        self.tooltip.refresh_text()

