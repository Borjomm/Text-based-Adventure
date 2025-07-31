from prompt_toolkit.layout import Container, Window
from abc import abstractmethod

import globals as g

from util import NormalizedKeyBindings


class AbstractScreen:
    def __init__(self, parent):
        self.parent = parent
        self._container = None
        self.set_keybindings()

    @abstractmethod
    def refresh_all(self):
        pass

    @abstractmethod
    def _build_container(self) -> Container:
        pass

    @property
    def container(self):
        if self._container is None:
            self._container = self._build_container()
        return self._container
    
    @container.setter
    def container(self, container):
        self._container = container

    def regenerate_container(self):
        self.container = self._build_container()
        g.ui.redraw_layout()
    
    def get_keybindings(self) -> NormalizedKeyBindings:
        return self.kb

    def _get_default_keybindings(self) -> NormalizedKeyBindings:
        kb = NormalizedKeyBindings()

        @kb.add(g.config.keys.quit_key)
        def _(event):
            self.exit()

        return kb
    
    def spacer(self, height=1):
        return Window(height=height)
    
    def set_keybindings(self, override_kb = None):
        if isinstance(override_kb, NormalizedKeyBindings):
            self.kb = override_kb
        else:
            self.kb = self._get_default_keybindings()

    def exit(self):
        if isinstance(self.parent, AbstractScreen):
            g.ui.switch_screen(self.parent)
            g.ui.current_screen.refresh_all()
        else:
            g.logger.warning("Tried to exit to parent screen, parent is not an instance of 'AbstractScreen'")

    def cleanup(self):
        pass
