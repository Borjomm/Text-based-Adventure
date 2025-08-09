from prompt_toolkit.layout import HSplit, Window
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ui.ui_controller import UiController

from ui.widgets import MenuItem, TextItem, MenuContainer
from .abstract_screen import AbstractScreen
from .settings_screen import SettingsScreen
from .character_creation_screen import CharacterCreationScreen

from events.events import EnginePauseEvent
import globals as g
from util import NormalizedKeyBindings

class TitleScreen(AbstractScreen):
    def __init__(self, controller: "UiController", parent: Optional[AbstractScreen]):
        super().__init__(controller, parent)
        self.controller.ui_to_engine_queue.put_nowait(EnginePauseEvent())
        self.selected_index = 0
        
        

        # 1) Build menu items with keys and handlers
        self.menu_items = MenuContainer([
            MenuItem(key="ui.new_game", handler=self._start_new),
            MenuItem(key="ui.load_game", handler=self._load_game),
            MenuItem(key="ui.settings", handler=self._open_settings),
            MenuItem(key="ui.exit", handler=self._exit_game)
        ])

        # 2) Layout
        self.title = TextItem(key="ui.title", height=3)

        self.separator = Window(height=1, char="─")

        self.tooltip = TextItem(key="ui.tooltip_main")

        # 4) Initial paint
        self.refresh_all()
    
    def _get_default_keybindings(self) -> NormalizedKeyBindings:
        keys = g.config.keys
        kb = NormalizedKeyBindings()
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

        @kb.add(keys.quit_key)
        def _(event):
            self._init_exit()
        return kb
    
        

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

    def _start_new(self):
        # called when user hits Enter on “New game”
        g.logger.debug("New game")
        self.controller.switch_screen(CharacterCreationScreen(self.controller, self))

    def _load_game(self):
        g.logger.debug("Game loading")

    def _open_settings(self):
        g.logger.info("Settings accessed")
        self.controller.switch_screen(SettingsScreen(self.controller, self, in_game=False))


    def _init_exit(self):
        self.set_keybindings(self._exit_keybinds())
        self.tooltip.key="ui.tooltip_exit"

    def _abandon_exit(self):
        self.set_keybindings()
        self.tooltip.key="ui.tooltip_main"

    def _exit_game(self):
        g.logger.warning("Exiting")
        self.controller.exit_game()

    def _exit_keybinds(self) -> NormalizedKeyBindings:
        kb = NormalizedKeyBindings()
        keys = g.config.keys
        # Handler to CONFIRM the exit
        @kb.add(keys.yes_key) # Use 'y' for "yes" - more intuitive than a second 'q'
        def _(event):
            self._exit_game()

        # Handler to CANCEL the exit
        @kb.add(keys.no_key) # Use 'n' for "no"
        def _(event):
            self._abandon_exit()

        return kb
