# ./src/logger/subloggers/tool_logger.py

"""Structured logger for tool invocation events.

This module provides ToolLogger, a thin wrapper around Logger that
formats tool-specific events such as calls, results, and errors with
consistent colorized prefixes.

Example:
    Basic usage:
    ```
    from src.logger.subloggers.logger import Logger
    from src.logger.subloggers.tool_logger import ToolLogger

    log = ToolLogger(core=Logger("tool"))
    log.calling("search", {"query": "python"})
    log.result("search", '["result1", "result2"]')
    log.error("search", "Connection timed out")
    ```
"""

from src.logger.subloggers.logger import Logger
from src.logger.subloggers.colors import (
    GREEN, RED, CYAN, PINK, BOLD
)


class ToolLogger:
    """A structured logger for tool invocation lifecycle events.

    Wraps a Logger instance and emits consistently formatted,
    colorized messages for tool calls, their results, and errors.

    Attributes:
        PREFIX: Static label prepended to every tool log message.

    Example:
    ```
    core = Logger("tool")
    log = ToolLogger(core)
    log.calling("get_weather", {"city": "Berlin"})
    log.result("get_weather", '{"temp": 22}')
    ```
    """

    PREFIX: str = "[TOOL]"
    """Label prepended to every message emitted by this logger."""

    def __init__(self, core: Logger):
        """Initializes the tool logger with an underlying Logger instance.

        Args:
            core: A Logger instance used for all output.

        Example:
        ```
        log = ToolLogger(core=Logger("my_tools"))
        ```
        """
        self._core = core

    def calling(self, name: str, args: dict):
        """Logs a tool invocation with its arguments.

        Args:
            name: Name of the tool being called.
            args: Dictionary of arguments passed to the tool.

        Example:
        ```
        log.calling("search", {"query": "python"})
        # [TOOL] search called with {"query": "python"}
        ```
        """
        self._log(
            name,
            f" called with {self._core.colorize(str(args), CYAN)}"
        )

    def result(self, name: str, result: str):
        """Logs the result returned by a tool.

        Args:
            name: Name of the tool that produced the result.
            result: String-encoded output returned by the tool.

        Example:
        ```
        log.result("search", '["result1", "result2"]')
        # [TOOL] search returned: ["result1", "result2"]
        ```
        """
        self._log(
            name,
            f" returned: {self._core.colorize(result, CYAN)}"
        )

    def error(self, name: str, error: str):
        """Logs an error that occurred during tool execution.

        Args:
            name: Name of the tool that failed.
            error: Error message or description.

        Example:
        ```
        log.error("search", "Connection timed out")
        # [TOOL] search failed: Connection timed out
        ```
        """
        self._log(
            name,
            f" failed: {self._core.colorize(error, RED)}"
        )

    def _log(self, name: str, message: str):
        """Logs an info-level message with the colorized tool prefix and name.

        Args:
            name: Name of the tool, rendered in green.
            message: Suffix message appended after the tool name.

        Example:
        ```
        self._log("search", " called with {}")
        # [TOOL] search called with {}
        ```
        """
        self._core.info(
            f"{self.prefix} {self._core.colorize(name, GREEN)}"
            f" {message}"
        )

    @property
    def prefix(self) -> str:
        """Returns the colorized tool prefix string.

        Renders PREFIX in bold pink using the underlying Logger's
        colorize method.

        Returns:
            A bold pink ANSI-colored string of PREFIX.

        Example:
        ```
        print(log.prefix)  # \x1b[95m\x1b[1m[TOOL]\x1b[0m
        ```
        """
        return self._core.colorize(self.PREFIX, PINK, BOLD)
