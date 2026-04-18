import logging
import sys
from contextlib import contextmanager
from typing import Callable


class GuiLogHandler(logging.Handler):
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.callback(self.format(record))
        except Exception:
            self.handleError(record)


class QueueWriter:
    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.buffer = ""

    def write(self, message: str) -> None:
        if not message:
            return
        self.buffer += message.replace("\r", "\n")
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            line = line.strip()
            if line:
                self.callback(line)

    def flush(self) -> None:
        line = self.buffer.strip()
        if line:
            self.callback(line)
        self.buffer = ""


@contextmanager
def capture_runtime_output(callback: Callable[[str], None]):
    handler = GuiLogHandler(callback)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    root_logger = logging.getLogger()
    original_level = root_logger.level
    stdout_writer = QueueWriter(callback)
    stderr_writer = QueueWriter(callback)
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    root_logger.addHandler(handler)
    if root_logger.level > logging.INFO:
        root_logger.setLevel(logging.INFO)
    sys.stdout = stdout_writer
    sys.stderr = stderr_writer

    try:
        yield
    finally:
        stdout_writer.flush()
        stderr_writer.flush()
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        root_logger.removeHandler(handler)
        root_logger.setLevel(original_level)
