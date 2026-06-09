# ./src/tools/base.py

"""Base interface for tool implementations.

This module defines the abstract base class that all tool
implementations must inherit from, enforcing a consistent interface
for name, description, parameter schema, and execution.

Example:
    Implementing a custom tool:
    ```
    from src.tools.base import BaseTool
    from src.tools.schema import ToolSchema, PropertySchema

    class EchoTool(BaseTool):
        @property
        def name(self) -> str:
            return "echo"

        @property
        def description(self) -> str:
            return "Returns the input text unchanged."

        @property
        def parameters(self) -> ToolSchema:
            return ToolSchema(
                type="object",
                properties={"text": PropertySchema(type="string")},
                required=["text"]
            )

        def run(self, text: str) -> str:
            return text
    ```
"""

from abc import ABC, abstractmethod
from src.tools.schema import ToolSchema


class BaseTool(ABC):
    """Abstract base class for all tool implementations.

    Subclasses must implement `name`, `description`, `parameters`,
    and `run` to be usable by the agent.

    Example:
    ```
    class SearchTool(BaseTool):
        @property
        def name(self) -> str:
            return "search"

        @property
        def description(self) -> str:
            return "Searches the web for a query."

        @property
        def parameters(self) -> ToolSchema:
            return ToolSchema(
                type="object",
                properties={"query": PropertySchema(type="string")},
                required=["query"]
            )

        def run(self, query: str) -> str:
            ...
    ```
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the tool used in LLM function calls.

        Returns:
            A short snake_case string identifying the tool.

        Example:
        ```
        class MyTool(BaseTool):
            @property
            def name(self) -> str:
                return "my_tool"
        ```
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does.

        Used by the LLM to decide when to invoke the tool.

        Returns:
            A concise plain-text description of the tool's purpose.

        Example:
        ```
        @property
        def description(self) -> str:
            return "Fetches the current weather for a given city."
        ```
        """
        pass

    @property
    @abstractmethod
    def parameters(self) -> ToolSchema:
        """Defines the input parameter schema for the tool.

        Returns:
            A ToolSchema describing the expected parameters,
            their types, and which are required.

        Example:
        ```
        @property
        def parameters(self) -> ToolSchema:
            return ToolSchema(
                type="object",
                properties={"city": PropertySchema(type="string")},
                required=["city"]
            )
        ```
        """
        pass

    @abstractmethod
    def run(self, *args, **kwargs) -> str:
        """Executes the tool with the provided arguments.

        Args:
            *args: Positional arguments specific to the tool implementation.
            **kwargs: Keyword arguments specific to the tool implementation.

        Returns:
            A string-encoded result of the tool execution.

        Example:
        ```
        result = tool.run(city="Berlin")
        print(result)  # '{"temp": 22, "condition": "sunny"}'
        ```
        """
        pass
