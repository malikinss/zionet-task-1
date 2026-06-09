# ./src/tools/time_tool.py

"""Current date and time tool.

This module provides `TimeTool`, a `BaseTool` implementation that returns
the current date and time as a formatted string.

Example:
    Basic usage:
    ```
    from src.tools.time_tool import TimeTool

    tool = TimeTool()
    print(tool.run())  # "2024-03-15 14:32:01"
    ```
"""

from datetime import datetime
from src.tools.base import BaseTool
from src.tools.schema import ToolSchema

DATE_FORMAT: str = "%Y-%m-%d"
"""strftime format string for the date portion of the output."""

TIME_FORMAT: str = "%H:%M:%S"
"""strftime format string for the time portion of the output."""


class TimeTool(BaseTool):
    """A tool that returns the current date and time as a string.

    Takes no input parameters and returns a single formatted timestamp
    combining `DATE_FORMAT` and `TIME_FORMAT`.

    Example:
    ```
    tool = TimeTool()
    tool.run()  # "2024-03-15 14:32:01"
    ```
    """

    @property
    def name(self) -> str:
        """Returns the tool identifier used in LLM function calls.

        Returns:
            The string `"get_current_time"`.

        Example:
        ```
        tool.name  # "get_current_time"
        ```
        """
        return "get_current_time"

    @property
    def description(self) -> str:
        """Returns a short description of the tool for the LLM.

        Returns:
            A plain-text description of the tool's purpose.

        Example:
        ```
        tool.description  # "Get the current date and time"
        ```
        """
        return "Get the current date and time"

    @property
    def parameters(self) -> ToolSchema:
        """Returns the parameter schema for this tool.

        This tool accepts no input parameters.

        Returns:
            A ToolSchema with an empty properties dict.

        Example:
        ```
        tool.parameters.properties  # {}
        ```
        """
        return ToolSchema(type="object", properties={})

    def run(self) -> str:
        """Returns the current date and time as a formatted string.

        Returns:
            A string combining DATE_FORMAT and TIME_FORMAT,
            e.g. `"2024-03-15 14:32:01"`.

        Example:
        ```
        tool.run()  # "2024-03-15 14:32:01"
        ```
        """
        return datetime.now().strftime(f"{DATE_FORMAT} {TIME_FORMAT}")
