from dataclasses import dataclass
from typing import Callable, Optional
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Window, HSplit

from util import parse_text, NormalizedKeyBindings

from .text_item import TextItem
from .setting_item import SettingItem
from ..layouts.abstract_screen import AbstractScreen

import globals as g

@dataclass(kw_only=True)
class SelectionMenuItem(TextItem):
    """A fallout list of options. Selecting an item causes
    on_close handler to execute with the option selected"""
    options: list[SettingItem]
    selected_index: int
    screen: AbstractScreen
    on_close_handler: Optional[Callable[[str], None]] = None

    def __post_init__(self):
        if not self.options:
            raise ValueError("SelectionMenuItem requires at least one option.")
        self.options_len = len(self.options)
        self._closed_text = self.get_closed_text()
        self._closed_control = FormattedTextControl(text=parse_text(self._closed_text), focusable=False)
        self.control = self._closed_control
        self._closed_window = Window(content=self._closed_control, height=self.height, cursorline=False, always_hide_cursor=True)
        self.window = self._closed_window
        self.opened = False
        self._last_index = self.selected_index

    def get_closed_text(self) -> str:
        """Get localized string of the item"""
        return f"{g.loc.translate(self.key)} - {g.loc.translate(self.options[self.selected_index].key)}"

    def refresh_text(self, selected: bool) -> None:
        if not self.opened:
            self._refresh_closed_text(selected)
        else:
            self._refresh_options()

    def _refresh_closed_text(self, selected: bool) -> None:
        self._closed_text = self.get_closed_text()
        if selected:
            text = parse_text(f"[green]{self._closed_text} <[reset]")
        else:
            text = parse_text(self._closed_text)
        self.control.text = text

    def handler(self) -> None:
        if self.opened:
            return
        self.opened = True
        g.logger.debug(f"List opened - {self.key}")
        self.window = self._build_opened()
        self._last_index = self.selected_index
        self.screen.set_keybindings(self._get_keybindings())
        self.screen.regenerate_container()

    def get_option(self) -> str:
        return self.options[self.selected_index].option
        
    def close_menu(self, canceled=False, **kwargs) -> None:
        if canceled:
            self.selected_index = self._last_index
        else:
            if self.on_close_handler is not None:
                self.on_close_handler(self.get_option(), **kwargs)
                
        self.opened = False
        g.logger.debug(f"List closed - {self.key}")
        self.window = self._closed_window
        self._refresh_closed_text(selected=True)
        self.screen.set_keybindings()
        self.screen.regenerate_container()

    def _get_keybindings(self) -> NormalizedKeyBindings:
        kb = NormalizedKeyBindings()
        keys = g.config.keys

        @kb.add(keys.arr_up)
        def _(event):
            self.selected_index = (self.selected_index - 1) % self.options_len
            self._refresh_options()

        @kb.add(keys.arr_down)
        def _(event):
            self.selected_index = (self.selected_index + 1) % self.options_len
            self._refresh_options()

        @kb.add(keys.enter_key)
        def _(event):
            self.close_menu()

        @kb.add(keys.quit_key)
        def _(event):
            self.close_menu(canceled=True)

        return kb

    def _build_text(self) -> list:
        option_list = []
        pre_text = f"{self.get_text()}"
        indent = " " * len(pre_text)
        for id, item in enumerate(self.options):
            if id == self.selected_index:
                text = f'[green] → {item.get_text()}[reset]'
            else:
                text = f'   {item.get_text()}'
                
            text = pre_text + text if id == 0 else indent + text

            option_list.append(text)
        return option_list

    def _build_opened(self) -> HSplit:
        entries = self._build_text()
        self.entry_controls = []  # Store the controls to update later

        windows = []
        for entry in entries:
            control = FormattedTextControl(text=parse_text(entry, prefix=self.prefix), focusable=False)
            self.entry_controls.append(control)
            window = Window(control, height=self.height)
            windows.append(window)

        return HSplit(windows)
    
    def _refresh_options(self) -> None:
        entries = self._build_text()
        for control, entry in zip(self.entry_controls, entries):
            control.text = parse_text(entry, prefix=self.prefix)

    def __len__(self) -> int:
        return len(self.options)