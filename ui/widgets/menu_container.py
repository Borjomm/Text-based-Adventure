
from dataclasses import dataclass
from typing import Optional, Any, Union, Callable
from .text_item import TextItem
from prompt_toolkit.layout import Window

import globals as g

@dataclass
class MenuContainer:
    items: list[Optional[TextItem]]
    is_selectable: bool = True
    refreshes_index: bool = False
    enable_input: bool = True
    def __post_init__(self):
        try:
            self.selected_index = self._find_next_interactive(-1, 1)
        except StopIteration:
            self.selected_index = 0
        self.selectable = self.is_selectable

    def _find_next_interactive(self, start, direction=1):
        idx = start
        for _ in range(len(self.items)):

            idx = (idx + direction) % len(self.items)
            item = self.items[idx]
            if isinstance(item, TextItem) and item.is_selectable:
                return idx
        
        raise StopIteration()
    
    @property
    def selectable(self) -> bool:
        return self._selectable
    
    @selectable.setter
    def selectable(self, val: bool) -> None:
        if self.refreshes_index:
            try:
                self.selected_index = self._find_next_interactive(-1, 1)
            except StopIteration:
                self.selected_index = 0
                g.logger.warning("Menu Container was enabled but no selectable items were found")
        self._selectable = val
        self.refresh_text()

    def next(self):
        self.selected_index = self._find_next_interactive(self.selected_index, 1)

    def previous(self):
        self.selected_index = self._find_next_interactive(self.selected_index, -1)

    def refresh_text(self):
        for i, item in enumerate(self.items):
            if isinstance(item, TextItem):
                item.refresh_text(i == self.selected_index and self.selectable)

    def toggle_input(self, value: bool):
        self.enable_input = value
        for item in self.items:
            if isinstance(item, TextItem):
                item.active = value

    def get_current_item(self) -> Optional[TextItem]:
        item = self.items[self.selected_index]
        return item if isinstance(item, TextItem) else None

    def exec(self) -> Any:
        if self.enable_input:
            item = self.items[self.selected_index]
            if isinstance(item, TextItem) and callable(getattr(item, "handler", None)):
                if item.active:
                    return item.handler()
            else:
                g.logger.warning(f"Tried to execute non-interactive item at index {self.selected_index}")


    def get_windows(self):
        windows = []
        for item in self.items:
            if item is None:
                windows.append(Window(height=1))  # default spacer
            elif isinstance(item, Window):
                windows.append(item)
            else:
                windows.append(item.window)
        return windows