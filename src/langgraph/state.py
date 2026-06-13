# ./src/langgraph/state.py

"""State definitions for the `LangGraph` agent.

This module defines the `AgentState` `TypedDict` used as the shared state
object across all nodes in the `LangGraph` agent graph, along with a
helper for extracting the last message.

Example:
    Initializing a state dict:
    ```
    from src.langgraph.state import AgentState

    state: AgentState = {
        "messages": [HumanMessage(content="Hello")],
        "tools_used": [],
        "iterations": 0,
    }
    ```
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage


class AgentState(TypedDict):
    """Shared state passed between nodes in the LangGraph agent graph.

    Attributes:
        messages: Accumulated conversation messages, merged automatically
            via the add_messages reducer on each graph step.
        tools_used: Names of all tools invoked so far in the current run.
        iterations: Number of LLM iterations completed so far.

    Example:
    ```
    state: AgentState = {
        "messages": [HumanMessage(content="What time is it?")],
        "tools_used": [],
        "iterations": 0,
    }
    ```
    """

    messages: Annotated[list, add_messages]
    tools_used: list[str]
    iterations: int


def last_message(state: AgentState | dict) -> AIMessage:
    """Returns the last message from the agent state.

    Args:
        state: The current agent state, either as an `AgentState`
            `TypedDict` or a plain dict with a `messages` key.

    Returns:
        The last element of the messages list, typically an AIMessage
        produced by the most recent LLM call.

    Example:
    ```
    msg = last_message(state)
    print(msg.content)  # "The current time is 14:32:01"
    ```
    """
    return state["messages"][-1]
