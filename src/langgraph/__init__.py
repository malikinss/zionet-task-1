# ./src/langgraph/__init__.py

"""Public API for the `LangGraph` agent package.

This module re-exports the `run` function as the sole intended entry
point for invoking the `LangGraph`-based agent.

Example:
    Importing from the package directly:
    ```
    from src.langgraph import run

    response = run("What is the weather in Tokyo?")
    print(response.answer)
    ```
"""

from .agent import run

__all__ = ["run"]
