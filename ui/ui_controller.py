from prompt_toolkit import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.key_binding import merge_key_bindings, DynamicKeyBindings
from prompt_toolkit.filters import Condition
from typing import Optional
import asyncio

from ui.layouts import TitleScreen, AbstractScreen, BattleScreen
from .ui_event_parser import UiEventParser

from events.events import EngineStopEvent
import globals as g
from util import NormalizedKeyBindings


class UiController:
    def __init__(self, engine_to_ui_queue: asyncio.Queue, ui_to_engine_queue: asyncio.Queue):
        self.keybind_override = False
        self.log_displayed = False
        self.event_parser = UiEventParser(engine_to_ui_queue, self)
        self.ui_to_engine_queue = ui_to_engine_queue
        self.battle_screen: Optional[BattleScreen] = None
        self.closing = False

        self.build_global_keybindings()

        self.current_screen = TitleScreen(self, None)
        self.previous_screen = self.current_screen
        self.layout = Layout(
            self.current_screen.container
        )
        self.app = Application(
            layout=self.layout,
            key_bindings=DynamicKeyBindings(self.get_keybindings),
            full_screen=True,
            cursor=None,
            refresh_interval=1/g.config.main.refresh_rate
        )
        g.logger.info(f"Window refresh rate set to {g.config.main.refresh_rate} FPS")
        g.loc.subscribe(self, self.current_screen.refresh_all)

    def redraw_layout(self):
        self.layout = Layout(
            self.current_screen.container
        )
        self.app.layout = self.layout
        self.current_screen.refresh_all()

    def switch_screen(self, screen: AbstractScreen):
        self.previous_screen = self.current_screen
        self.current_screen = screen
        self.redraw_layout()
        
    def exit_game(self):
        self.closing = True
        g.loc.unsubscribe(self)
        self.ui_to_engine_queue.put_nowait(EngineStopEvent())

    def get_keybindings(self):
        
        kb = self.global_kb if self.log_displayed else merge_key_bindings([self.global_kb, self.current_screen.get_keybindings()])
        return kb
    
    def build_global_keybindings(self):
        """
        Recreates the global keybindings from the current config.
        This ensures that any changes to keybinds are applied.
        """
        self.global_kb = NormalizedKeyBindings()

        @self.global_kb.add(g.config.keys.log_key, filter=Condition(lambda: not self.keybind_override))
        def _(event):
            self.toggle_log()

    def toggle_log(self):
        self.log_displayed = not self.log_displayed
        self.layout.container = g.logger.container if self.log_displayed else self.current_screen.container

    def broadcast_cleanup(self):
        """
        Walks down the screen stack from the current screen and calls
        the cleanup method on each one to ensure all background tasks are stopped.
        """
        g.logger.debug("Broadcasting cleanup signal through the screen stack.")
        screen = self.current_screen
        while screen:
            if hasattr(screen, 'cleanup') and callable(screen.cleanup):
                screen.cleanup()
            
            # Move to the parent screen in the stack
            # Check if parent is another screen or the UiController itself
            if hasattr(screen, 'parent') and isinstance(screen.parent, AbstractScreen):
                screen = screen.parent
            else:
                # Reached the top of the stack (or a screen with no parent)
                break
