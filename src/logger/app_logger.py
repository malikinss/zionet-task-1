# ./src/logger/app_logger.py

"""Application-level logger composing all structured sub-loggers.

This module provides AppLogger, a single entry point that lazily
instantiates and exposes AgentLogger and ToolLogger, both sharing
one underlying Logger core.

Example:
    Basic usage:
    ```
    from src.logger.app_logger import AppLogger

    log = AppLogger("my_app")
    log.agent.start("What is 2 + 2?")
    log.tool.calling("calculator", {"expression": "2 + 2"})
    log.tool.result("calculator", "4")
    log.agent.final_answer("4")
    ```
"""

from src.logger.subloggers import Logger, AgentLogger, ToolLogger


class AppLogger:
    """A composite logger exposing typed sub-loggers for agent and tool events.

    Lazily instantiates AgentLogger and ToolLogger on first access,
    both sharing a single underlying Logger core.

    Attributes:
        _core: Shared Logger instance used by all sub-loggers.
        _agent: Cached AgentLogger instance, created on first access.
        _tool: Cached ToolLogger instance, created on first access.

    Example:
    ```
    log = AppLogger("pipeline")
    log.agent.start("Translate this text")
    log.tool.calling("translate", {"text": "Hello", "lang": "fr"})
    log.agent.final_answer("Bonjour")
    ```
    """

    def __init__(self, name: str = "app"):
        """Initializes the AppLogger with a named core Logger.

        Args:
            name: Name passed to the underlying Logger. Defaults to
                  `"app"`.

        Example:
        ```
        log = AppLogger()
        log = AppLogger("worker")
        ```
        """
        self._core = Logger(name)
        self._agent = None
        self._tool = None

    @property
    def agent(self) -> AgentLogger:
        """Returns the AgentLogger, creating it on first access.

        Returns:
            A shared AgentLogger instance backed by the core Logger.

        Example:
        ```
        log.agent.start("Summarize this document")
        log.agent.iteration(1)
        ```
        """
        return self._get_logger("_agent", AgentLogger)

    @property
    def tool(self) -> ToolLogger:
        """Returns the ToolLogger, creating it on first access.

        Returns:
            A shared ToolLogger instance backed by the core Logger.

        Example:
        ```
        log.tool.calling("search", {"query": "AI"})
        log.tool.result("search", '["result1"]')
        ```
        """
        return self._get_logger("_tool", ToolLogger)

    def _get_logger(self, attr_name: str, logger_type):
        """Returns a cached sub-logger, instantiating it if not yet created.

        Args:
            attr_name: Name of the instance attribute used to cache
                the sub-logger (e.g. `"_agent"`).
            logger_type: Class to instantiate if the cached value is
                None. Must accept a single Logger argument.

        Returns:
            An instance of `logger_type` stored on this object.

        Example:
        ```
        agent = self._get_logger("_agent", AgentLogger)
        tool = self._get_logger("_tool", ToolLogger)
        ```
        """
        logger = getattr(self, attr_name, None)
        if logger is None:
            logger = logger_type(self._core)
            setattr(self, attr_name, logger)
        return logger
