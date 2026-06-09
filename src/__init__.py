# ./src/__init__.py

"""Public API for the src package.

This module re-exports the top-level classes intended for use by
consumers of the package, providing a single stable import point
for the agent and its response schema.

Example:
    Importing from the package directly:
    ```
    from src import Agent, AgentResponse

    agent = Agent()
    response: AgentResponse = agent.run("What is the capital of France?")
    print(response.answer)      # "Paris"
    print(response.tools_used)  # []
    print(response.iterations)  # 1
    ```
"""

from src.agent import Agent
from src.schemas import AgentResponse

__all__ = [
    "Agent",
    "AgentResponse"
]
