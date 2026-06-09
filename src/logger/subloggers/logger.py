# ./src/logger/subloggers/logger.py

"""Logger module providing a colored console logging wrapper.

This module defines the Logger class, which wraps Python's standard
logging library and adds colored terminal output via ColoredFormatter.

Example:
    Basic usage:
    ```
        from src.logger.subloggers.logger import Logger

        log = Logger("my_app")
        log.info("Application started")
        log.separator()
        log.error("Something went wrong")
    ```
"""

import logging
import os
from src.logger.subloggers.formatter import ColoredFormatter
from src.logger.subloggers.colors import GREEN, RESET

LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
"""Default log level, read from the LOG_LEVEL environment variable.

Falls back to "INFO" if the variable is not set.

Example:
    Override via environment before running:
    ```
        $ LOG_LEVEL=DEBUG python main.py
    ```
"""


class Logger:
    """A colored console logger wrapping Python's standard logging.

    Configures a StreamHandler with ColoredFormatter and disables
    propagation to parent loggers.

    Attributes:
        _logger (logging.Logger): Underlying standard library logger instance.

    Example:
    ```
    log = Logger("service", level="DEBUG")
    log.debug("Initializing service")
    log.info("Service is ready")
    log.separator(char="-", length=40)
    ```
    """

    def __init__(self, name: str, level: str = LOG_LEVEL):
        """Initializes the logger with the given name and level.

        Args:
            name: Logger name passed to logging.getLogger.
            level: Logging level as a string. Defaults to the module-level
                LOG_LEVEL constant.

        Example:
        ```
        log = Logger("auth", level="WARNING")
        ```
        """
        self._logger = logging.getLogger(name)
        self._logger.propagate = False
        self._logger.setLevel(level.upper())
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter())
        self._logger.addHandler(handler)

    def debug(self, msg: str):
        """Logs a message at DEBUG level.

        Args:
            msg: Message text to log.

        Example:
        ```
        log.debug("Fetching user from database")
        ```
        """
        self._logger.debug(msg)

    def info(self, msg: str):
        """Logs a message at INFO level.

        Args:
            msg: Message text to log.

        Example:
        ```
        log.info("Server started on port 8080")
        ```
        """
        self._logger.info(msg)

    def warning(self, msg: str):
        """Logs a message at WARNING level.

        Args:
            msg: Message text to log.

        Example:
        ```
        log.warning("Config file not found, using defaults")
        ```
        """
        self._logger.warning(msg)

    def error(self, msg: str):
        """Logs a message at ERROR level.

        Args:
            msg: Message text to log.

        Example:
        ```
        log.error("Failed to connect to database")
        ```
        """
        self._logger.error(msg)

    def separator(self, char: str = "=", length: int = 60):
        """Logs a horizontal separator line at INFO level.

        Args:
            char: Character used to build the separator. Defaults to "=".
            length: Number of times the character is repeated. Defaults to 60.

        Example:
        ```
        log.separator()         # ==================...
        log.separator("-", 5)   # -----
        ```
        """
        self.info(self.colorize(char * length, GREEN))

    def colorize(self, message: str, color: str, bold: str = "") -> str:
        """Wraps a message in ANSI color and optional bold codes.

        Args:
            message: Original message text.
            color: ANSI color code (e.g. GREEN).
            bold: ANSI bold code. Defaults to an empty string.

        Returns:
            The message string wrapped with ANSI codes and a reset suffix.

        Example:
        ```
        from src.logger.subloggers.colors import GREEN, BOLD
        colored = log.colorize("Success", GREEN, BOLD)
        ```
        """
        return f"{color}{bold}{message}{RESET}"
