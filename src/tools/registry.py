# ./src/tools/registry.py

"""Tool registry for managing and dispatching tool invocations.

This module provides `ToolRegistry`, a central store that registers
`BaseTool` instances, dispatches tool calls by name, and serializes
all registered tools into an LLM-compatible schema.

Example:
    Using the default registry:
    ```
    from src.tools.registry import ToolRegistry

    registry = ToolRegistry()
    print(registry.run("calculator", {"expr": "2 + 2"}))  # "2 + 2 = 4"
    print(registry.run("unknown_tool", {})) # "Unknown tool: unknown_tool"
    ```

    Using a custom set of tools:
    ```
    from src.tools.registry import ToolRegistry
    from src.tools.calculator import CalculatorTool

    registry = ToolRegistry(tools=[CalculatorTool()])
    schema = registry.to_tools_schema()
    ```
"""

from typing import Optional
from src.tools.base import BaseTool
from src.tools.weather import WeatherTool
from src.tools.calculator import CalculatorTool
from src.tools.time_tool import TimeTool

DEFAULT_TOOLS: list[BaseTool] = [WeatherTool(), CalculatorTool(), TimeTool()]
"""Default tool instances registered when no tools are provided."""


class ToolRegistry:
    """A registry that stores, dispatches, and serializes tools.

    Registers BaseTool instances by name on initialization and
    provides methods to invoke them by name and export their
    schemas for use in LLM API calls.

    Attributes:
        _tools: Internal mapping from tool name to BaseTool instance.

    Example:
    ```
    registry = ToolRegistry()
    registry.register(MyCustomTool())
    result = registry.run("my_custom_tool", {"arg": "value"})
    schema = registry.to_tools_schema()
    ```
    """

    def __init__(self, tools: Optional[list[BaseTool]] = None):
        """Initializes the registry and registers the provided tools.

        Args:
            tools: List of `BaseTool` instances to register. Defaults to
                `DEFAULT_TOOLS` if not provided.

        Example:
        ```
        registry = ToolRegistry()
        registry = ToolRegistry(tools=[CalculatorTool()])
        ```
        """
        self._tools: dict[str, BaseTool] = {}
        self._register_init_tools(tools or DEFAULT_TOOLS)

    def _register_init_tools(self, tools: list[BaseTool]):
        """Registers a list of tools by iterating and calling register.

        Args:
            tools: List of `BaseTool` instances to register.

        Example:
        ```
        self._register_init_tools([CalculatorTool(), TimeTool()])
        ```
        """
        for tool in tools:
            self.register(tool)

    def register(self, tool: BaseTool):
        """Adds a tool to the registry under its name.

        If a tool with the same name is already registered, it will
        be silently overwritten.

        Args:
            tool: A `BaseTool` instance to register.

        Example:
        ```
        registry.register(WeatherTool())
        registry.register(CalculatorTool())
        ```
        """
        self._tools[tool.name] = tool

    def run(self, name: str, args: dict) -> str:
        """Dispatches a tool call by name with the given arguments.

        Args:
            name: Name of the tool to invoke.
            args: Keyword arguments to pass to the tool's run method.

        Returns:
            The string result of the tool execution, or an error
            message if the tool name is not registered.

        Example:
        ```
        registry.run("calculator", {"expr": "10 * 3"})  # "10 * 3 = 30"
        registry.run("missing", {}) # "Unknown tool: missing"
        ```
        """
        if name not in self._tools:
            return f"Unknown tool: {name}"
        return self._tools[name].run(**args)

    def to_tools_schema(self) -> list[dict]:
        """Serializes all registered tools into LLM-compatible schema dicts.

        Returns:
            A list of dicts, one per registered tool, each containing
            `name`, `description`, and `parameters` in JSON
            Schema format.

        Example:
        ```
        schema = registry.to_tools_schema()
        # [
        #   {"name": "calculator", "description": "...", "parameters": {...}},
        #   ...
        # ]
        ```
        """
        return [self._declare_tool(t) for t in self._tools.values()]

    @staticmethod
    def _declare_tool(t: BaseTool) -> dict:
        """Converts a single `BaseTool` into an LLM-compatible schema dict.

        Args:
            t: A `BaseTool` instance to serialize.

        Returns:
            A dict with keys `name`, `description`, and
            `parameters`, where `parameters` follows JSON Schema
            object format with `type`, `properties`, and
            `required`.

        Example:
        ```
        ToolRegistry._declare_tool(CalculatorTool())
            # {
            #     "name": "calculator",
            #     "description": "Safely evaluate a math expression",
            #     "parameters": {
            #         "type": "object",
            #         "properties": {"expr": {"type": "string"}},
            #         "required": ["expr"]
            #     }
            # }
        ```
        """
        return {
            "name": t.name,
            "description": t.description,
            "parameters": {
                "type": t.parameters.type,
                "properties": {
                    k: {"type": v.type}
                    for k, v in t.parameters.properties.items()
                },
                "required": t.parameters.required or [],
            },
        }
