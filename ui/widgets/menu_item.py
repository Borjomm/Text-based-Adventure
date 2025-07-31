from dataclasses import dataclass
from typing import Callable

from .text_item import TextItem
from util.text_renderer import parse_text

import globals as g



@dataclass(kw_only=True)
class MenuItem(TextItem):
    handler: Callable[[], None]         # function to call on Enter
    prompt: str = " <"
    selection_tag: str = "[green]"
    inactive_selection_tag: str = "[yellow]"
    active: bool = True

    def __post_init__(self):
        # Need to call parent's __post_init__ to initialize control & window
        super().__post_init__()

    def refresh_text(self, selected: bool) -> None:
        raw = self.get_text()
        if selected:
            selection_tag = self.selection_tag if self.active else self.inactive_selection_tag
            self.control.text = parse_text(f"{selection_tag}{raw}{self.prompt}[reset]", prefix = self.prefix)
        else:
            self.control.text = parse_text(raw, prefix=self.prefix)
    