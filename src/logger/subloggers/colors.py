# ./src/logger/subloggers/colors.py

"""ANSI color and style codes for terminal output.

This module defines ANSI escape sequences used to colorize log output
in the terminal, and a mapping from standard log level names to their
associated colors.

Example:
    Using colors directly:
    ```
    from src.logger.subloggers.colors import GREEN, BOLD, RESET
    print(f"{BOLD}{GREEN}Success{RESET}")
    ```

    Using the level mapping:
    ```
    from src.logger.subloggers.colors import LEVELS
    color = LEVELS.get("WARNING")
    print(f"{color}Something looks off{RESET}")
    ```
"""

CYAN: str = "\x1b[36m"
"""ANSI escape code for cyan text."""

YELLOW: str = "\x1b[33m"
"""ANSI escape code for yellow text."""

MAGENTA: str = "\x1b[35m"
"""ANSI escape code for magenta text."""

PINK: str = "\x1b[95m"
"""ANSI escape code for bright magenta (pink) text."""

RESET: str = "\x1b[0m"
"""ANSI escape code to reset all text formatting."""

BOLD: str = "\x1b[1m"
"""ANSI escape code for bold text."""

GREY: str = "\x1b[90m"
"""ANSI escape code for dark grey (bright black) text."""

GREEN: str = "\x1b[32m"
"""ANSI escape code for green text."""

RED: str = "\x1b[31m"
"""ANSI escape code for red text."""

LEVELS: dict[str, str] = {
    "DEBUG":    CYAN,
    "INFO":     GREEN,
    "WARNING":  YELLOW,
    "ERROR":    RED,
    "CRITICAL": MAGENTA,
}
"""Mapping from log level names to their ANSI color codes.

Example:
```
    color = LEVELS["ERROR"]
    print(f"{color}Something failed{RESET}")
```
"""
