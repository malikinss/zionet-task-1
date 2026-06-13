# ./src/langgraph/agent.py

"""`LangGraph`-based agent entry point.

This module builds and compiles a `LangGraph` `StateGraph` that alternates
between LLM calls and tool executions, and exposes a run function as
the public interface for invoking the agent.

Example:
    Basic usage:
    ```
    from src.langgraph.agent import run

    response = run("What is the weather in Paris and 10 * 42?")
    print(response.answer)
    print(response.tools_used)   # ["get_weather", "calculator"]
    print(response.iterations)   # 3
    ```
"""

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from src.langgraph.state import AgentState, last_message
from src.langgraph.nodes import call_llm, call_tools, should_continue
from src.schemas import AgentResponse
from src.prompts import SYSTEM_PROMPT


def _build_graph():
    """Constructs and compiles the `LangGraph` `StateGraph` for the agent.

    Registers the `llm` and `tools` nodes, sets `llm` as the
    entry point, adds a conditional edge from `llm` via
    `should_continue`, and connects `tools` back to `llm`.

    Returns:
        A compiled `LangGraph` application ready to invoke.

    Example:
    ```
    app = _build_graph()
    result = app.invoke({...})
    ```
    """
    graph = StateGraph(AgentState)
    graph.add_node("llm", call_llm)
    graph.add_node("tools", call_tools)
    graph.set_entry_point("llm")
    graph.add_conditional_edges(
        "llm", should_continue, {"tools": "tools", END: END}
    )
    graph.add_edge("tools", "llm")
    return graph.compile()


_app = _build_graph()
"""Compiled `LangGraph` application instance, built once at import time."""


def run(user_prompt: str) -> AgentResponse:
    """Runs the `LangGraph` agent for the given user prompt.

    Invokes the compiled graph with an initial state containing the
    system prompt and the user message. Attempts to parse the last
    message content as a JSON-encoded `AgentResponse`. Falls back to
    using the raw content string if parsing fails.

    Args:
        user_prompt: The user's input message to the agent.

    Returns:
        An `AgentResponse` containing the final answer, list of tool
        names used, and total iteration count.

    Example:
    ```
    response = run("What is 25 * 48 and the current time?")
    print(response.answer)
    print(response.tools_used)   # ["calculator", "get_current_time"]
    print(response.iterations)   # 3
    ```
    """
    result = _app.invoke({
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ],
        "tools_used": [],
        "iterations": 0,
    })
    last = last_message(result)
    content = str(last.content) if last.content else ""
    try:
        parsed = AgentResponse.model_validate_json(content)
        return AgentResponse(
            answer=parsed.answer,
            tools_used=result["tools_used"],
            iterations=result["iterations"],
        )
    except Exception:
        return AgentResponse(
            answer=content,
            tools_used=result["tools_used"],
            iterations=result["iterations"],
        )
