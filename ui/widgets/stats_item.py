from dataclasses import dataclass, field
from typing import Callable
from .menu_item import MenuItem

from events.event_containers import EntityContainer
from util import parse_text

import globals as g

@dataclass
class StatsItem(MenuItem):
    entity: EntityContainer
    handler: Callable[[], None] = field(init=False)
    
    def __post_init__(self):
        # Need to call parent's __post_init__ to initialize control & window
        super().__post_init__()
        self.handler = self.return_entity_id
        self.template_dict: dict = self._update_dict_info()

    def _update_dict_info(self):
        return {
            "NAME": self.entity.get_name(),
            "HP": self.entity.health,
            "MAX_HP": self.entity.max_health,
            "AP": self.entity.ap,
            "MAX_AP": self.entity.max_ap,
            "ATTACK": self.entity.attack
        }

    def refresh_text(self, selected: bool = False) -> None:
        self.template_dict = self._update_dict_info()
        raw = self.get_text()
        if selected:
            selection_tag = self.selection_tag if self.active else self.inactive_selection_tag
            self.control.text = parse_text(f"{selection_tag}{raw}{self.prompt}[reset]", format_template=self.template_dict, prefix=self.prefix)
        else:
            self.control.text = parse_text(raw, format_template=self.template_dict, prefix=self.prefix)

    def return_entity_id(self):
        return self.entity.entity_id
    