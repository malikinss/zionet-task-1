# ./src/logger/subloggers/formatter.py

"""Colored log formatter for terminal output.

This module provides a custom logging.Formatter subclass that applies
ANSI color codes to log records based on their severity level.

Example:
    Attaching the formatter to a handler:
    ```
    import logging
    from src.logger.subloggers.formatter import ColoredFormatter

    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter())

    logger = logging.getLogger("app")
    logger.addHandler(handler)
    logger.warning("Low disk space")
    # [14:32:01] [WARNING] Low disk space  ← yellow
    ```
"""

import logging
from src.logger.subloggers.colors import (LEVELS, GREY, BOLD, RESET)

TIME_FORMAT: str = "%H:%M:%S"
"""strftime format string used to render the timestamp in log records."""


class ColoredFormatter(logging.Formatter):
    """A logging formatter that colorizes output using ANSI escape codes.

    Each log record is rendered as a single line containing a grey
    timestamp, a bold level tag, and a message — all colored according
    to the level defined in `LEVELS`. Falls back to `RESET` for
    unrecognized levels.

    Attributes:
        FORMAT: Template string used to compose each log line.

    Example:
    ```
    import logging
    from src.logger.subloggers.formatter import ColoredFormatter

    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter())
    logger = logging.getLogger("demo")
    logger.addHandler(handler)
    logger.error("Something broke")
    # [09:15:42] [ERROR] Something broke  ← red
    ```
    """

    FORMAT: str = (
        "{grey}[{time}]{reset} "
        "{color}{bold}[{level}]{reset} "
        "{color}{msg}{reset}"
    )
    """Log line template with named placeholders for colors and content."""

    def format(self, record: logging.LogRecord) -> str:
        """Formats a log record into a colorized single-line string.

        Looks up the ANSI color for the record's level name in `LEVELS`,
        then interpolates all color codes, the timestamp, level name,
        and message into `FORMAT`.

        Args:
            record: The log record to format, as produced by the
                standard logging machinery.

        Returns:
            A fully formatted string with ANSI color codes applied,
            ready for terminal output.

        Example:
        ```
        import logging
        formatter = ColoredFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0,
            msg="Server ready", args=(), exc_info=None
        )
        print(formatter.format(record))
        # [10:00:00] [INFO] Server ready  ← green
        ```
        """
        color = LEVELS.get(record.levelname, RESET)
        return self.FORMAT.format(
            grey=GREY,
            reset=RESET,
            bold=BOLD,
            color=color,
            time=self.formatTime(record, TIME_FORMAT),
            level=record.levelname,
            msg=record.getMessage(),
        )
