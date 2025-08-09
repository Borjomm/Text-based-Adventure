from dataclasses import dataclass, field
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.layout import Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import D
from util import parse_text, NormalizedKeyBindings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ui.ui_controller import UiController
    from ..layouts import AbstractScreen

from .text_item import TextItem
import globals as g

@dataclass(kw_only=True)
class TextInputItem(TextItem):
    key: str
    screen: "AbstractScreen"
    controller: "UiController"
    default: str = ""
    height: int = 1
    width: int | None = None
    is_selectable: bool = True

    _text: str = field(init=False)
    _editing: bool = field(init=False, default=False)
    _last_selection: bool = field(init=False, default=False)

    # Controls and windows
    _label_control: FormattedTextControl = field(init=False)
    _label_window: Window = field(init=False)
    _input_area: TextArea = field(init=False)
    _input_vsplit: VSplit = field(init=False)

    window: Window | VSplit = field(init=False)

    def __post_init__(self):
        self._text = self.default

        # Label for normal (non-editing) mode
        self._label_control = FormattedTextControl(
            text=self._get_label_text(selected=False),
            focusable=False
        )
        self._label_window = Window(
            content=self._label_control,
            height=self.height,
            always_hide_cursor=True
        )

        # TextArea for editing
        self._input_area = TextArea(
            text=self._text,
            multiline=False,
            wrap_lines=False,
            height=D.exact(self.height),
            width=self.width,
            prompt=""
        )

        # Label Window (static) for edit mode
        self._edit_label_window = Window(
            content=FormattedTextControl(
                text=parse_text(f"{g.loc.translate(self.key)}: ", prefix=self.prefix),
                focusable=False
            ),
            dont_extend_width=True,
            always_hide_cursor=True
        )

        # VSplit containing label + input area
        self._input_vsplit = VSplit([
            self._edit_label_window,
            self._input_area
        ])

        # Start in label mode
        self.window = self._label_window

    def _get_label_text(self, selected: bool) -> str:
        bridge = " - " if self._text else ": "
        label = g.loc.translate(self.key) + bridge + self._text
        return parse_text(f"[green]{label} <[reset]", prefix=self.prefix) if selected else parse_text(label, prefix=self.prefix)

    def refresh_text(self, selected: bool = False):
        self._last_selection = selected
        if not self._editing:
            self._label_control.text = self._get_label_text(selected)

    def get_text(self) -> str:
        return self._text
    
    def _get_keybindings(self) -> NormalizedKeyBindings:
        kb = NormalizedKeyBindings()
        keys = g.config.keys

        @kb.add(keys.enter_key)
        def _(event):
            self.close_menu()

        return kb

    def close_menu(self, canceled=False):
        # Confirm and exit edit mode
        self._text = self._input_area.text
        self._editing = False
        self.window = self._label_window
        self.refresh_text(selected=True)
        self.screen.set_keybindings()
        self.screen.regenerate_container()
        self.controller.keybind_override = False

    def handler(self):
        self._editing = True
        self._input_area.text = self._text
        self._input_area.buffer.cursor_position = len(self._text)
        self.window = self._input_vsplit
        self.screen.set_keybindings(self._get_keybindings())
        self.screen.regenerate_container()
        self.controller.app.layout.focus(self._input_area)
        self.controller.keybind_override = True
            # Enter edit mode
            
