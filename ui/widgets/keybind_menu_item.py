from dataclasses import dataclass, field
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from ui.ui_controller import UiController

from .text_item import TextItem
from ..layouts.abstract_screen import AbstractScreen

from util import parse_text, CYRILLIC_TO_LATIN, NormalizedKeyBindings

import globals as g

@dataclass(kw_only=True)
class KeybindMenuItem(TextItem):
    config_key: str
    screen: AbstractScreen
    controller: "UiController"
    on_close_handler: Callable[[], None] = None
    waiting_for_key: bool = field(init=False, default=False)
    h_offset:int = 0
    
    def __post_init__(self):
        super().__post_init__()

    def get_text(self) -> str:
        return f"{g.loc.translate(self.key)} - [{self.config_key}]"

    def refresh_text(self, selected: bool = False) -> None:
        raw_text = self.get_text()
        if selected:
            self.control.text = parse_text(f"{' '*self.h_offset}[green]{raw_text} <[reset]", prefix=self.prefix)
        else:
            self.control.text = parse_text(f"{' '*self.h_offset}{raw_text}", prefix=self.prefix)

    def handler(self) -> None:
        if self.waiting_for_key:
            return
        self.waiting_for_key = True
        prompt_text = f"Press a new key for {g.loc.translate(self.key)} or [quit_key] to cancel..."
        self.control.text = parse_text(f"[yellow]{prompt_text}", prefix=self.prefix)
        self.controller.keybind_override = True

        kb = NormalizedKeyBindings()

        @kb.add(g.config.keys.quit_key)
        def _(event):
            self.waiting_for_key = False
            self.refresh_text(selected=True)
            self.screen.set_keybindings()
            self.controller.keybind_override = False

        @kb.add("<any>")
        def _(event):
            raw_key = event.key_sequence[0].key.lower()
            normalized_key = CYRILLIC_TO_LATIN.get(raw_key, raw_key)
            setattr(g.config.keys, self.config_key, normalized_key)
            self.waiting_for_key = False
            self.controller.build_global_keybindings()
            self.screen.set_keybindings()
            self.screen.refresh_all()
            self.controller.keybind_override = False

        self.screen.set_keybindings(kb)
