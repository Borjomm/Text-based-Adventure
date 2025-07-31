from __future__ import annotations
from .abstract_screen import AbstractScreen

from ..widgets import KeybindMenuItem, TextItem, MenuItem, SelectionMenuItem, SettingItem, MenuContainer

# 1. Add the import for Dimension
from prompt_toolkit.layout import HSplit, Window, VSplit
from prompt_toolkit.layout.dimension import D 

import globals as g

from global_state.consts import LANGUAGES
from events.events import GameStopEvent

class SettingsScreen(AbstractScreen):
    def __init__(self, parent):
        super().__init__(parent)
        language_options = [SettingItem(key=f"ui.{lang}", option=lang) for lang in LANGUAGES]
        self.selected_index = 0
        self.selected_h_index = 0
        self.title = TextItem(key="ui.settings", height=1)
        self.separator = Window(height=1, char="─")
        self.blank = Window(height=1)
        self.tooltip = TextItem(key="ui.tooltip_settings")
        self.back = MenuItem(key="ui.back", handler=self.exit)
        self.to_title = MenuItem(key="ui.to_title", handler=self.to_title_screen)
        
        # 2. When creating MenuItems, pass width=D()
        #    (Assuming you updated MenuItem to accept a `width` parameter)
        self.menu_tabs: list[TextItem] = [
            MenuItem(key="ui.controls", handler=None, prompt="", selection_tag="[bold][green]"),
            MenuItem(key="ui.language", handler=None, prompt="", selection_tag="[bold][green]")
        ]
        
        self.tab_containers: list[list[TextItem]] = [
            [KeybindMenuItem(key=f"ui.{key}", config_key=key, screen=self) for key, entry in g.config.keys.option_dict.items() if not entry.fixed],
            [SelectionMenuItem(
                key="ui.change_language",
                screen=self, 
                options=language_options, 
                selected_index=LANGUAGES.index(g.config.main.language), 
                on_close_handler=g.loc.set_language)]
        ]
        self.set_tab_container()
        self.refresh_all()

    def set_tab_container(self):
        list_container = [
            *self.tab_containers[self.selected_h_index],
            None,
            self.back,
            None
        ]
        if g.engine.is_running():
            list_container.append(self.to_title)
        self.current_menu_container = MenuContainer(list_container)
    
    @property
    def menu_items(self):
        return self.current_menu_container
    
    def exit(self):
        super().exit()
        g.config.save()

    def to_title_screen(self):
        from .title_screen import TitleScreen
        g.config.save()
        g.ui.battle_screen = None
        g.ui.ui_to_engine_queue.put_nowait(GameStopEvent())
        g.ui.broadcast_cleanup()
        g.ui.switch_screen(TitleScreen(g.ui))

    # 3. Update the _build_container method
    def _build_container(self):
        # Build the list of tab windows and add a flexible spacer at the end
        tab_layout_items = [item.window for item in self.menu_tabs]
        tab_layout_items.append(Window(width=D())) 

        return HSplit([
            self.title.window,
            self.separator,
            VSplit(tab_layout_items, padding=3),
            self.separator,
            *self.menu_items.get_windows(),
            self.separator,
            self.tooltip.window
        ])

    def _get_default_keybindings(self):
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

        @kb.add(keys.tab_key)
        def _(evt):
            self.selected_h_index = (self.selected_h_index + 1) % len(self.menu_tabs)
            self.set_tab_container()  # 👈 re-create on tab switch only
            self.regenerate_container()
            self.refresh_all()

        @kb.add(keys.enter_key)
        def _(evt):
            self.menu_items.exec()

        return kb
    
    def refresh_all(self):
        for idx, item in enumerate(self.menu_tabs):
            item.refresh_text(idx == self.selected_h_index)
        self.title.refresh_text()
        self.menu_items.refresh_text()
        self.tooltip.refresh_text()