
from prompt_toolkit.layout import HSplit, FormattedTextControl, Window
from prompt_toolkit.widgets import Frame
from prompt_toolkit.formatted_text import to_formatted_text, FormattedText
from collections import deque
from dataclasses import dataclass
from typing import List
import asyncio

from events.events import BattleLogEvent, RefreshLogEvent
from util import parse_text

import globals as g

@dataclass
class LogWindow:
    title_key: str
    max_entries: int
    placeholder_text: str = "ui.empty"
    typewriter_delay: float = 0.05
    fast_typeriter_delay: float = 0.005
    """
    A simple log window that displays the last `max_entries` log messages.
    """
    def __post_init__(self):
        # initialize control + window
        localized_placeholder_text = g.loc.translate(self.placeholder_text)
        self.logs:deque[BattleLogEvent] = deque(maxlen=self.max_entries)
        self.controls = [FormattedTextControl(text=localized_placeholder_text, focusable=False) for _ in range(self.max_entries)]
        self.log_windows = [Window(content=control, height=1, cursorline=False, always_hide_cursor=True) for control in self.controls]
        self.window = Frame(HSplit(self.log_windows), title=g.loc.translate(self.title_key))
        self.writing = False
        self._log_queue: asyncio.Queue[BattleLogEvent] = asyncio.Queue()
        self._log_task = asyncio.create_task(self._process_log_queue())

    async def accept_new_log(self, event_list: List[BattleLogEvent]):
        self.logs:deque[BattleLogEvent] = deque(event_list, max_len=self.max_entries)
        self.refresh_log()

    async def log(self, event: BattleLogEvent) -> None:
        """
        Append a message to the log and refresh the display.
        """
        await self._log_queue.put(event)

    async def _process_log_queue(self) -> None:
        """
        Continuously processes log events one by one.
        """
        while True:
            event = await self._log_queue.get()
            try:
                if isinstance(event, BattleLogEvent):
                    self.logs.append(event)
                    await self._update_log(write_new=True)
                elif isinstance(event, RefreshLogEvent):
                    self.window.title = g.loc.translate(self.title_key)
                    await self._update_log()
            except Exception as e:
                g.logger.warning(f"Error while processing log event: {e}")
            finally:
                self._log_queue.task_done()

    async def _update_log(self, write_new: bool = False) -> None:
        while self.writing:
            await asyncio.sleep(0.1)

        # --- Step 1: Clear all controls for a clean slate ---
        localized_placeholder_text = g.loc.translate(self.placeholder_text)
        for control in self.controls:
            control.text = parse_text(localized_placeholder_text)

        # --- Step 2: Determine which logs and controls to update instantly ---
        
        # The total number of logs we will have on screen
        total_logs_to_display = len(self.logs)
        
        # The UI control index where the first log should appear
        start_render_index = self.max_entries - total_logs_to_display
        
        # The list of logs that will be rendered instantly (not typewritten)
        entries_to_render_instantly = list(self.logs)
        if write_new:
            # If writing a new one, don't include the very last log in the instant render
            entries_to_render_instantly = entries_to_render_instantly[:-1]

        # --- Step 3: Render the instant logs in the correct position ---
        
        # The slice of controls that corresponds to the instant-render logs
        # It starts at the calculated start_render_index and has a length
        # equal to the number of logs we're rendering instantly.
        num_instant_logs = len(entries_to_render_instantly)
        instant_controls_slice = self.controls[start_render_index : start_render_index + num_instant_logs]
        
        # Create the message texts for these logs
        messages = [parse_text(g.loc.translate(entry.message_key), format_template=entry.data_dict) for entry in entries_to_render_instantly]
        
        # Zip and update the controls
        for control, message in zip(instant_controls_slice, messages):
            control.text = message
            
        g.ui.app.invalidate()

        # --- Step 4: If there's a new log, typewrite it into the last position ---
        if write_new and self.logs:
            # The last control is always at index -1
            last_control = self.controls[-1]
            await self._typewrite(self.logs[-1], last_control)

    

    async def _typewrite(
        self,
        event: BattleLogEvent,
        control: FormattedTextControl
    ) -> None:
        """
        Writes the content of an ANSI object to a FormattedTextControl
        with a typewriter effect.

        Args:
            ansi_object: The ANSI object containing the styled text to write.
            control: The FormattedTextControl to write to.
            delay: The time in seconds to wait between each character.
            clear_before_start: If True, clears the control's text before starting.
        """
        self.writing = True
        app = g.ui.app # Get the current prompt_toolkit application instance
        localized_str = g.loc.translate(event.message_key)
        ansi_object = parse_text(localized_str, format_template=event.data_dict)

        current_output_parts: list[tuple[str, str]] = []

        control.text = FormattedText([]) # Clear the control
        app.invalidate()
        self.writing = True
        await asyncio.sleep(0.01) # Small delay for initial clear to render

        # CORRECTED LINE: Use to_formatted_text to get the iterable FormattedText object
        parsed_formatted_text = to_formatted_text(ansi_object)
        for style, text_segment in parsed_formatted_text:
            for char in text_segment:
                current_output_parts.append((style, char))
                control.text = FormattedText(current_output_parts)
                app.invalidate() # Force a redraw of the UI
                await asyncio.sleep(self.typewriter_delay if not self._log_queue.qsize() > 0 else self.fast_typeriter_delay)
        await asyncio.sleep(0.5)

        # Optional: ensure the final text is set exactly from the ANSI object
        # This also works correctly with parsed_formatted_text as it's a FormattedText object.
        control.text = parsed_formatted_text
        app.invalidate()
        self.writing = False

    def cleanup(self):
        """Cancels the background processing task."""
        if self._log_task and not self._log_task.done():
            self._log_task.cancel()
            g.logger.debug("LogWindow's background task cancelled.")