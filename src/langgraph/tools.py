# ./src/langgraph/tools.py

"""`LangChain` tool wrappers for use in the `LangGraph` agent.

This module wraps the core `BaseTool` implementations as `LangChain`
tools using the `@tool` decorator, and exposes a list and a name-keyed
map of all available tools for use in the agent graph.

Example:
    Invoking a tool directly:
    ```
    from src.langgraph.tools import get_weather, calculator, TOOL_MAP

    print(get_weather.invoke({"city": "Berlin"}))
    # "Berlin, Germany: Partly cloudy, 18°C, humidity 72%, wind 14.4 kph"

    tool = TOOL_MAP["calculator"]
    print(tool.invoke({"expr": "2 ** 10"}))
    # "2 ** 10 = 1024"
    ```
"""

from langchain_core.tools import tool
from src.tools import BaseTool
from src.tools.weather import WeatherTool
from src.tools.calculator import CalculatorTool
from src.tools.time_tool import TimeTool

_weather = WeatherTool()
"""Module-level instance reused across all get_weather calls."""

_calculator = CalculatorTool()
"""Module-level instance reused across all calculator calls."""

_time = TimeTool()
"""Module-level instance reused across all get_current_time calls."""


@tool
def get_weather(city: str) -> str:
    """Get current real weather for a given city."""
    return _weather.run(city)


@tool
def calculator(expr: str) -> str:
    """Safely evaluate a math expression."""
    return _calculator.run(expr)


@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return _time.run()


TOOLS: list = [get_weather, calculator, get_current_time]
"""All registered LangChain tools available to the agent graph."""

TOOL_MAP: dict[str, BaseTool] = {t.name: t for t in TOOLS}
"""Mapping from tool name to `LangChain` tool instance."""
