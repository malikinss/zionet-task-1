# ./src/schemas.py

"""Pydantic response schemas for the agent.

This module defines the structured output models returned by the
agent after completing a run.

Example:
    Constructing a response:
    ```
    from src.schemas import AgentResponse

    response = AgentResponse(
        answer="The current time is 14:32:01",
        tools_used=["get_current_time"],
        iterations=2
    )
    print(response.model_dump())
    ```
"""

from pydantic import BaseModel


class AgentResponse(BaseModel):
    """Structured result returned by the agent after completing a run.

    Attributes:
        answer: The final answer produced by the agent.
        tools_used: Names of all tools invoked during the run.
        iterations: Total number of LLM iterations performed.

    Example:
    ```
    response = AgentResponse(
        answer="Paris",
        tools_used=["search"],
        iterations=3
    )
    print(response.answer)       # "Paris"
    print(response.tools_used)   # ["search"]
    print(response.iterations)   # 3
    ```
    """
    answer: str
    tools_used: list[str]
    iterations: int
