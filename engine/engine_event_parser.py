from __future__ import annotations
from typing import TYPE_CHECKING

import asyncio
if TYPE_CHECKING:
    from .engine import GameEngine

from events.events import GameStartEvent, PlayerActionEvent, GameStopEvent, EnginePauseEvent, EngineResumeEvent, EngineStopEvent

class EngineEventParser:
    def __init__(self, ui_to_engine_queue: asyncio.Queue, controller: GameEngine):
        self.ui_to_engine_queue = ui_to_engine_queue
        self.engine = controller

    async def process_events(self):
        while not self.engine.closing:
            # Use queue.get_nowait() so the engine doesn't block if there are no UI events
            event = await self.ui_to_engine_queue.get()
            # Process the player's action
            match event:
                case GameStartEvent():
                    name = event.player_name
                    p_class = event.player_class
                    self.engine.initialize_world()
                    self.engine.create_player(name=name, player_class=p_class)
                    self.engine.start_game()
                case PlayerActionEvent():
                    if self.engine.battle_running:
                        asyncio.create_task(self.engine.battle_resolver.execute_player_action(event))
                case GameStopEvent():
                    self.engine.stop_game()
                case EnginePauseEvent():
                    self.engine.pause()
                case EngineResumeEvent():
                    self.engine.resume()
                case EngineStopEvent():
                    self.engine.stop()

