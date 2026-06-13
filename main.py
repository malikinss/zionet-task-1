# ./main.py

"""Entry point for comparing `Agent` and `LangGraph` agent implementations.

This script runs the same multi-tool prompt through both the custom
`Agent` and the `LangGraph`-based agent, printing each result as formatted
`JSON`. Exits with code `1` if any unhandled exception occurs.

Example:
    Running directly:
    ```
    $ python main.py
    ```
"""

import json
import sys
from src.agent import Agent
from src.langgraph import run as lg_run
from src.logger import AppLogger


logger = AppLogger("main")
"""Module-level logger used to report fatal errors in main."""


def main():
    """Runs both agent implementations against a shared multi-tool prompt.

    Instantiates the custom `Agent` and invokes both it and the `LangGraph`
    agent via `test_request`. Logs the error and exits with code `1` on
    any unhandled exception.

    Raises:
        SystemExit: With exit code `1` if either agent raises an exception.

    Example:
    ```
    main()
    # [Agent] Final JSON Response: {...}
    # [LangGraph] Final JSON Response: {...}
    ```
    """
    try:
        agent = Agent()
        test_request(agent.run, "Agent")
        test_request(lg_run, "LangGraph")
    except Exception as e:
        logger.agent.error(f"Fatal error: {e}")
        sys.exit(1)


def test_request(run_func, name: str) -> None:
    """Runs a multi-tool prompt through a given agent function and prints
    the result.

    Args:
        run_func: A callable that accepts a prompt string and returns
            an `AgentResponse`.
        name: Display name of the agent implementation, used as a
            label in the printed output.

    Example:
    ```
    test_request(agent.run, "Agent")
    # [Agent] Final JSON Response:
    # {
    #   "answer": "...",
    #   "tools_used": ["get_weather", "calculator", "get_current_time"],
    #   "iterations": 4
    # }
    ```
    """
    result = run_func(
        "What is the weather in London and Tokyo? "
        "Also, what is 25 * 48? "
        "And what is the current time?"
    )
    print(f"\n[{name}] Final JSON Response: ")
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
