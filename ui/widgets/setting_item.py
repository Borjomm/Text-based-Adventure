from dataclasses import dataclass

from .text_item import TextItem

@dataclass(kw_only=True)
class SettingItem(TextItem):
    option: str

    def __post_init__(self):
        super().__post_init__()