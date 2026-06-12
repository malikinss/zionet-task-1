# ./src/langgraph/nodes.py

"""`LangGraph` node functions and routing logic for the agent graph.

This module defines the LLM call node, the tool execution node, and
the conditional edge function that decides whether to continue with
tool calls or terminate the graph.

Example:
    Using nodes in a `StateGraph`:
    ```
    from langgraph.graph import StateGraph
    from src.langgraph.nodes import call_llm, call_tools, should_continue
    from src.langgraph.state import AgentState

    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.add_node("tools", call_tools)
    graph.add_conditional_edges("llm", should_continue)
    ```
"""

import os
from langchain_core.messages import ToolMessage
from langchain_groq import ChatGroq
from src.langgraph.state import AgentState, last_message
from src.langgraph.tools import TOOLS, TOOL_MAP
from langgraph.graph import END

DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
"""Fallback Groq model name used when `GROQ_MODEL_NAME` is not set."""

MODEL: str = os.getenv("GROQ_MODEL_NAME", DEFAULT_MODEL)
"""Active Groq model name, resolved from the environment at import time."""

llm = ChatGroq(model=MODEL).bind_tools(TOOLS)
"""Module-level LLM instance with all tools bound, reused across calls."""


def call_llm(state: AgentState) -> AgentState:
    """Invokes the LLM with the current message history.

    Passes the full message list from state to the LLM and returns
    an updated state with the response appended and the iteration
    counter incremented.

    Args:
        state: The current agent state containing `messages`, `tools_used`,
            and `iterations`.

    Returns:
        An updated `AgentState` with the LLM response added to `messages`
        and `iterations` incremented by 1.

    Example:
    ```
    state = {
        "messages": [HumanMessage(content="Hi")],
        "tools_used": [],
        "iterations": 0
    }
    new_state = call_llm(state)
    print(new_state["iterations"])  # 1
    ```
    """
    response = llm.invoke(state["messages"])
    return {
        "messages": [response],
        "tools_used": state["tools_used"],
        "iterations": state["iterations"] + 1,
    }


def call_tools(state: AgentState) -> AgentState:
    """Executes all tool calls requested in the last LLM message.

    Reads tool calls from the last message, invokes each tool via
    `TOOL_MAP`, and returns an updated state with the tool results
    appended as `ToolMessages` and tool names recorded.

    Args:
        state: The current agent state whose last message contains
            one or more tool calls.

    Returns:
        An updated `AgentState` with `ToolMessage` results added to
        `messages` and all invoked tool names appended to `tools_used`.

    Example:
    ```
    new_state = call_tools(state)
    print(new_state["tools_used"])   # ["get_weather"]
    print(new_state["messages"][-1]) # ToolMessage(content="Berlin, ...")
    ```
    """
    last = last_message(state)
    results = []
    tools_used = list(state["tools_used"])
    for tc in last.tool_calls:
        result = TOOL_MAP[tc["name"]].invoke(tc["args"])
        tools_used.append(tc["name"])
        results.append(ToolMessage(content=result, tool_call_id=tc["id"]))
    return {
        "messages": results,
        "tools_used": tools_used,
        "iterations": state["iterations"],
    }


def should_continue(state: AgentState) -> str:
    """Determines whether the graph should continue to tool execution or end.

    Checks if the last message contains any tool calls. Returns
    `"tools"` to route to the tool execution node, or `END` to
    terminate the graph.

    Args:
        state: The current agent state whose last message is inspected
            for tool calls.

    Returns:
        The string `"tools"` if tool calls are present, or `END`
        if the LLM produced a final text answer.

    Example:
    ```
    route = should_continue(state)
    print(route)  # "tools" or END
    ```
    """
    last = last_message(state)
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END
