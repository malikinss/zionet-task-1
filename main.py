# ./main.py

"""Entry point for running the agent with a sample multi-tool prompt.

This script instantiates the `Agent` with default settings and runs it
against a prompt that exercises weather lookup, arithmetic, and time
retrieval in a single query. The final structured response is printed
as formatted JSON.

Example:
    Running directly:
    ```
    $ python main.py
    ```
"""

import json
from src.agent import Agent


def main():
    """Runs the agent with a sample multi-tool prompt and prints the result.

    Instantiates `Agent` with default LLM, registry, and logger, then
    calls run with a prompt covering weather, calculator, and time
    tools. Prints the final `AgentResponse` as indented JSON. Silently
    suppresses any exceptions.

    Example:
    ```
    main()
    # 📊 Final JSON Response:
    # {
    #   "answer": "...",
    #   "tools_used": ["get_weather", "calculator", "get_current_time"],
    #   "iterations": 4
    # }
    ```
    """
    agent = Agent()

    try:
        result = agent.run(
            "What is the weather in London and Tokyo? "
            "Also, what is 25 * 48? "
            "And what is the current time?"
        )
        print("\n📊 Final JSON Response:")
        print(json.dumps(result.model_dump(), indent=2))
    except Exception:
        pass


if __name__ == "__main__":
    main()
