from engine.engine import GameEngine
from config.config import Config
from logger.log_screen import Logger
from ui.ui_controller import UiController
from ui.translator import LocalizationManager

import globals as g

import asyncio

class Client:
    def __init__(self, argv):
        keep_log = "--keep-log" in argv

        # Parse log level from args
        log_level = "DEBUG"
        for i, arg in enumerate(argv):
            if arg in ("--log", "--log-level") and i + 1 < len(argv):
                log_level = argv[i + 1]

        self.engine_to_ui_queue = asyncio.Queue()
        self.ui_to_engine_queue = asyncio.Queue()

        self.logger = Logger(log_level, keep_log)
        g.logger = self.logger

        self.config = Config()
        g.config = self.config

        self.loc = LocalizationManager(lang=g.config.main.language)
        g.loc = self.loc
        
        self.ui = UiController(self.engine_to_ui_queue, self.ui_to_engine_queue)
        g.ui = self.ui

        self.engine = GameEngine(self.ui_to_engine_queue, self.engine_to_ui_queue)
        g.engine = self.engine

    async def run(self):
        await asyncio.gather(
            self.engine.tick(),
            self.ui.app.run_async(),
            self.ui.event_parser.process_events(),
            self.engine.event_parser.process_events()
        )

    def launch(self):
        asyncio.run(self.run())

