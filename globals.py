from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logger.log_screen import Logger
    from config.config import Config
    from ui.ui_controller import UiController
    from engine.engine import GameEngine
    from ui.translator import LocalizationManager
    from global_state.client import Client

client: Client = None
logger: Logger = None
config: Config = None
ui: UiController = None
engine: GameEngine = None
loc: LocalizationManager = None