from dataclasses import dataclass

from .menu_item import MenuItem
from events.event_containers import AbilityContainer

from util.text_renderer import parse_text

import globals as g

@dataclass(kw_only=True)
class AbilityItem(MenuItem):
    container: AbilityContainer

    def __post_init__(self):
        # Need to call parent's __post_init__ to initialize control & window
        super().__post_init__()

    def refresh_text(self, selected: bool) -> None:
        raw = self.get_text()
        
        if self.container.ap == 0:
            ap_key = g.loc.translate("abilities.null_ap")
        elif self.container.ap > 0:
            ap_key = g.loc.translate("abilities.consume_ap")
        elif self.container.ap < 0:
            ap_key = g.loc.translate("abilities.give_ap")
        
        self.container.data_dict["AP"] = abs(self.container.ap)

        if selected:
            selection_tag = self.selection_tag if self.active else self.inactive_selection_tag
            self.control.text = parse_text(f"{selection_tag}{raw}{ap_key}{self.prompt}[reset]", prefix = self.prefix, format_template=self.container.data_dict)
        else:
            self.control.text = parse_text(f"{raw}{ap_key}", prefix=self.prefix, format_template=self.container.data_dict)