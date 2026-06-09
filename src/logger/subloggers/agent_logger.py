# ./src/logger/subloggers/agent_logger.py

"""Structured logger for agent lifecycle events.

This module provides AgentLogger, a thin wrapper around Logger that
formats agent-specific events such as prompt start, iteration steps,
final answers, and errors with consistent colorized prefixes.

Example:
    Basic usage:
    ```
    from src.logger.subloggers.logger import Logger
    from src.logger.subloggers.agent_logger import AgentLogger

    log = AgentLogger(core=Logger("agent"))
    log.start("What is the capital of France?")
    log.iteration(1)
    log.final_answer("Paris")
    ```
"""

from src.logger.subloggers.logger import Logger
from src.logger.subloggers.colors import (
    CYAN, YELLOW, MAGENTA, PINK, BOLD
)


class AgentLogger:
    """A structured logger for agent lifecycle events.

    Wraps a Logger instance and emits consistently formatted,
    colorized messages for the key stages of an agent run.

    Attributes:
        PREFIX: Static label prepended to every agent log message.

    Example:
    ```
    core = Logger("agent")
    log = AgentLogger(core)
    log.start("Summarize this document")
    log.iteration(1)
    log.final_answer("Here is the summary...")
    ```
    """

    PREFIX: str = "[AGENT]"
    """Label prepended to every message emitted by this logger."""

    def __init__(self, core: Logger):
        """Initializes the agent logger with an underlying Logger instance.

        Args:
            core: A Logger instance used for all output.

        Example:
        ```
        log = AgentLogger(core=Logger("my_agent"))
        ```
        """
        self._core = core

    def start(self, prompt: str):
        """Logs the beginning of an agent run with the initial prompt.

        Emits a separator, a "Starting" message, and the prompt text,
        followed by another separator.

        Args:
            prompt: The user prompt that initiated the agent run.

        Example:
        ```
        log.start("What is the weather in Berlin?")
        # ============================================================
        # [AGENT] Starting
        # [AGENT] Prompt: What is the weather in Berlin?
        # ============================================================
        ```
        """
        self._core.separator()
        self._log("Starting")
        self._log(f"Prompt: {self._core.colorize(prompt, CYAN)}")
        self._core.separator()

    def iteration(self, n: int):
        """Logs the start of an agent iteration.

        Args:
            n: The current iteration number.

        Example:
        ```
        log.iteration(3)
        # [AGENT] Iteration 3
        ```
        """
        self._log(f"Iteration {self._core.colorize(str(n), YELLOW)}")

    def final_answer(self, answer: str):
        """Logs the agent's final answer surrounded by separators.

        Args:
            answer: The final answer produced by the agent.

        Example:
        ```
        log.final_answer("The capital of France is Paris.")
        # ============================================================
        # [AGENT] Final answer: The capital of France is Paris.
        # ============================================================
        ```
        """
        self._core.separator()
        self._log(f"Final answer: {self._core.colorize(answer, MAGENTA)}")
        self._core.separator()

    def error(self, msg: str):
        """Logs an error message at ERROR level with the agent prefix.

        Args:
            msg: Error message text.

        Example:
        ```
        log.error("Tool execution failed")
        # [AGENT] Tool execution failed
        ```
        """
        self._core.error(f"{self.prefix} {msg}")

    def _log(self, msg: str):
        """Logs an info-level message with the colorized agent prefix.

        Args:
            msg: Message text to log.

        Example:
        ```
        self._log("Thinking...")
        # [AGENT] Thinking...
        ```
        """
        self._core.info(f"{self.prefix} {msg}")

    @property
    def prefix(self) -> str:
        """Returns the colorized agent prefix string.

        Renders PREFIX in bold pink using the underlying Logger's
        colorize method.

        Returns:
            A bold pink ANSI-colored string of PREFIX.

        Example:
        ```
        print(log.prefix)  # \x1b[95m\x1b[1m[AGENT]\x1b[0m
        ```
        """
        return self._core.colorize(self.PREFIX, PINK, BOLD)
