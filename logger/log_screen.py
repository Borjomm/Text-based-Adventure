from prompt_toolkit.layout import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from datetime import datetime
import inspect

from util.text_renderer import parse_text

from global_state.consts import LOG_FILE, MAX_LOG_FILE_SIZE

import os

class Logger:
    MAX_ENTRIES = 30

    def __init__(self, level: str, keep_log=False):
        
        level = level.upper()
        self._entries: list[str] = []
        self._displayed_entries: list[str] = []
        self.write_info = True
        self.write_debug = True

        self.log_control = FormattedTextControl(
            text=self._get_display_text()
        )
        self.log_window = Window(content=self.log_control, always_hide_cursor=True)

        self.container = HSplit([self.log_window])
        if not keep_log:
            self.clear_log_file()
        self.set_level(level)

    def clear_log_file(self):
        try:
            open(LOG_FILE, "w", encoding="utf-8").close()
                
        except Exception as e:
            self.warning(f"Failed to clear log file: {e}")

    def set_level(self, level):
        if level == "DEBUG":
            self.write_info = True
            self.write_debug = True
        elif level == "INFO":
            self.write_info = True
            self.write_debug = False
        elif level == "WARNING":
            self.write_info = False
            self.write_debug = False
        else:
            self.warning(f"Logger: Expected INFO/DEBUG/WARNING as argument, got '{level}'. Launching with level 'INFO'")
            return self.set_level("INFO")
        self.info(f"Logger initialized with level {level}.")
        


    def _format(self, text:str, level:int) -> str:
        stack = inspect.stack()
        caller_frame = stack[2+level] #Real function, not debug, warning or info
        return f"[{datetime.now().strftime('%H:%M:%S')}] - [{caller_frame.function}] {text}"

    def debug(self, text: str, level=0):
        if self.write_debug:
            processed_text = f"[yellow][DEBUG] - {self._format(text, level)}[reset]"
            self._add(processed_text)

    def warning(self, text, level=0):
        processed_text = f"[red][WARNING] - {self._format(text, level)}[reset]"
        self._add(processed_text)

    def info(self, text, level=0):
        if self.write_info:
            processed_text = f"[INFO] - {self._format(text, level)}"
            self._add(processed_text)

    def _add(self, processed_text:str):
        self._entries.append(processed_text)
        self._displayed_entries.append(processed_text)
        if len(self._displayed_entries) > self.MAX_ENTRIES:
            self._displayed_entries.pop(0)

        self.log_control.text = self._get_display_text()

        self._write_to_file(processed_text)

    def _write_to_file(self, line: str):
        try:
            if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_FILE_SIZE:
                os.rename(LOG_FILE, LOG_FILE + ".1")  # simple rotation
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(self._strip_formatting(line) + "\n")
        except Exception as e:
            # Avoid recursive logging
            pass

    
    def _strip_formatting(self, line: str) -> str:
        import re
        return re.sub(r'\[(yellow|red|green|reset)\]', '', line)


    def _get_display_text(self):
        """Convert entries to displayable formatted text (e.g. with newlines)."""
        return parse_text("\n".join(self._displayed_entries))