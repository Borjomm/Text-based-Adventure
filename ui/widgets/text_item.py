from dataclasses import dataclass, field
from typing import Callable

from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Window, WindowAlign
from prompt_toolkit.layout.dimension import D

from util import parse_text
import asyncio

import globals as g


@dataclass(kw_only=True)
class TextItem:
    _key: str = field(init=False, repr=False)
    key: str
    height: int = 1
    is_selectable: bool = True
    prefix: str = ""
    active: bool = True

    extra_width: int = 0
    control: FormattedTextControl = field(init=False)
    window:  Window               = field(init=False)

    def __post_init__(self):
        # initialize control + window
        self.control = FormattedTextControl(
            text=g.loc.translate(self.key),
            focusable=False
        )
        self.window = Window(
            content=self.control,
            height=self.height,
            cursorline=False,
            always_hide_cursor=True,
            align=self._get_alignment(),
            
        )

    def _get_alignment(self):
        if self.extra_width:
            return WindowAlign.CENTER
        return WindowAlign.LEFT
    
    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, new_key: str) -> None:
        self._key = new_key
        if hasattr(self, 'control'):
            self.refresh_text()

    def get_text(self) -> str:
        return g.loc.translate(self.key)

    def refresh_text(self, *args) -> None:
        self.control.text = parse_text(self.get_text(), prefix=self.prefix)

    def __str__(self) -> str:
        return self.get_text(self)
    
    def handler(self):
        pass

    def set_temp_key(self, new_key: str, time_amount: float) -> None:
        async def _temp_key(old_key, new_key, delay):
            self.key = new_key
            await asyncio.sleep(delay)
            self.key = old_key
        old_key = self.key
        asyncio.create_task(_temp_key(old_key, new_key, time_amount))