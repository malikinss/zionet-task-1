# ./src/agent.py

"""Core agent orchestrating LLM calls and tool invocations.

This module defines the Agent class, which drives a tool-calling loop:
it sends conversation history to the LLM, processes any requested tool
calls, appends results to the history, and repeats until the model
produces a final text answer.

Example:
    Basic usage with defaults:
    ```
    from src.agent import Agent

    agent = Agent()
    response = agent.run("What is the weather in Rome?")
    print(response.answer)
    print(response.tools_used)   # ["get_weather"]
    print(response.iterations)   # 2
    ```

    Custom LLM and registry:
    ```
    from src.agent import Agent
    from src.llm.gemini_client import GeminiClient
    from src.tools.registry import ToolRegistry
    from src.tools.calculator import CalculatorTool

    agent = Agent(
        llm=GeminiClient(),
        registry=ToolRegistry(tools=[CalculatorTool()]),
    )
    response = agent.run("What is 123 * 456?")
    ```
"""

import json
from typing import Optional
from dotenv import load_dotenv
from src.llm.base import BaseLLMClient
from src.llm.dto import HistoryEntry, ToolCallEntry, FunctionInfo, LLMResponse
from src.llm.groq_client import GroqClient
from src.tools.registry import ToolRegistry
from src.schemas import AgentResponse
from src.logger import AppLogger

LOGGER_NAME: str = "agent"
"""Default logger name used when no AppLogger is provided."""

load_dotenv()


class Agent:
    """An agent that drives a tool-calling loop with an LLM backend.

    Sends conversation history to the LLM, processes tool call
    requests by dispatching them through the ToolRegistry, and
    repeats until the model returns a plain-text final answer.

    Attributes:
        llm: LLM client used for content generation.
        registry: Tool registry used to dispatch tool calls.
        logger: Application logger for agent and tool events.

    Example:
    ```
    agent = Agent()
    response = agent.run("What time is it?")
    print(response.answer)      # "The current time is 14:32:01"
    print(response.tools_used)  # ["get_current_time"]
    ```
    """

    def __init__(
        self,
        llm: Optional[BaseLLMClient] = None,
        registry: Optional[ToolRegistry] = None,
        logger: Optional[AppLogger] = None
    ):
        """Initializes the agent with optional LLM, registry, and logger.

        Falls back to GroqClient, ToolRegistry, and AppLogger with
        LOGGER_NAME if any argument is not provided.

        Args:
            llm: LLM client to use for generation. Defaults to
                a GroqClient instance.
            registry: Tool registry to use for dispatching tool calls.
                Defaults to a `ToolRegistry` with `DEFAULT_TOOLS`.
            logger: Application logger. Defaults to an AppLogger
                named by `LOGGER_NAME`.

        Example:
        ```
        agent = Agent()
        agent = Agent(llm=GeminiClient(), registry=ToolRegistry())
        ```
        """
        self.llm = llm or GroqClient()
        self.registry = registry or ToolRegistry()
        self.logger = logger or AppLogger(LOGGER_NAME)

    def run(self, user_prompt: str) -> AgentResponse:
        """Runs the agent loop for the given user prompt.

        Initializes conversation history, then repeatedly calls the
        LLM and processes tool calls until a final text answer is
        returned.

        Args:
            user_prompt: The user's input message to the agent.

        Returns:
            An AgentResponse containing the final answer, list of
            tool names used, and total iteration count.

        Example:
        ```
        response = agent.run("What is 2 ** 10?")
        print(response.answer)      # "2 ** 10 = 1024"
        print(response.tools_used)  # ["calculator"]
        print(response.iterations)  # 2
        ```
        """
        self.logger.agent.start(user_prompt)
        history = self._init_history(user_prompt)
        tools = self.registry.to_tools_schema()
        tools_used: list[str] = []
        iterations = 0

        while True:
            iterations += 1
            self.logger.agent.iteration(iterations)
            response = self._call_llm(history, tools)

            if not response.has_tool_calls:
                return self._build_response(response, tools_used, iterations)

            self._process_tool_calls(response, history, tools_used)

    def _init_history(self, user_prompt: str) -> list:
        """Creates the initial conversation history from the user prompt.

        Args:
            user_prompt: The user's input message.

        Returns:
            A single-element list containing the user message as a
            serialized `HistoryEntry` dict.

        Example:
        ```
        self._init_history("Hello")
        # [{"role": "user", "content": "Hello"}]
        ```
        """
        return [HistoryEntry(role="user", content=user_prompt).to_dict()]

    def _call_llm(self, history: list, tools: list) -> LLMResponse:
        """Calls the LLM with the current history and tool schema.

        Logs the error via the agent logger and re-raises if the
        LLM call fails.

        Args:
            history: Current conversation history as a list of dicts.
            tools: List of tool schema dicts to pass to the LLM.

        Returns:
            An `LLMResponse` containing the model's text and tool calls.

        Raises:
            Exception: Any exception raised by the LLM client.

        Example:
        ```
        response = self._call_llm(history, tools)
        print(response.content)
        ```
        """
        try:
            return self.llm.generate(history, tools)
        except Exception as e:
            self.logger.agent.error(str(e))
            raise

    def _build_assistant_entry(self, response: LLMResponse) -> HistoryEntry:
        """Builds a HistoryEntry representing the assistant's tool call turn.

        Converts each `ToolCall` in the response into a `ToolCallEntry`
        with a serialized `FunctionInfo`, then wraps them in a
        `HistoryEntry` with role `"assistant"`.

        Args:
            response: The `LLMResponse` containing tool calls to convert.

        Returns:
            A `HistoryEntry` with role `"assistant"` and the tool calls
            attached.

        Example:
        ```
        entry = self._build_assistant_entry(response)
        entry.to_dict()
        # {"role": "assistant", "content": "", "tool_calls": [...]}
        ```
        """
        tool_calls = [
            ToolCallEntry(
                id=tc.id,
                type="function",
                function=FunctionInfo(
                    name=tc.name,
                    arguments=json.dumps(tc.args),
                ).to_dict(),
            )
            for tc in response.tool_calls
        ]
        return HistoryEntry(
            role="assistant",
            content=response.content or "",
            tool_calls=tool_calls,
        )

    def _process_tool_calls(
        self, response: LLMResponse, history: list, tools_used: list
    ) -> None:
        """Dispatches all tool calls in a response and appends results
        to history.

        Appends the assistant's tool call entry to history, then for
        each tool call: logs the invocation, runs it via the registry,
        logs the result, records the tool name, and appends the tool
        result to history.

        Args:
            response: The `LLMResponse` containing tool calls to process.
            history: Conversation history list, mutated in place.
            tools_used: List of tool names, mutated in place.

        Example:
        ```
        self._process_tool_calls(response, history, tools_used)
        # history now contains the assistant entry and tool results
        ```
        """
        history.append(self._build_assistant_entry(response).to_dict())
        for tc in response.tool_calls:
            args = tc.args or {}
            self.logger.tool.calling(tc.name, args)
            result = self.registry.run(tc.name, args)
            self.logger.tool.result(tc.name, result)
            tools_used.append(tc.name)
            tool_result = self.llm.build_tool_result(tc.id, tc.name, result)
            history.append(tool_result.to_dict())

    def _build_response(
        self, response: LLMResponse, tools_used: list, iterations: int
    ) -> AgentResponse:
        """Builds the final `AgentResponse` from the LLM's text answer.

        Logs the final answer and constructs an `AgentResponse` with
        the answer text, tools used, and iteration count.

        Args:
            response: The `LLMResponse` containing the final text answer.
            tools_used: List of tool names invoked during the run.
            iterations: Total number of LLM iterations performed.

        Returns:
            An `AgentResponse` with the final answer, tools used, and
            iteration count.

        Example:
        ```
        result = self._build_response(response, ["calculator"], 2)
        result.answer      # "2 + 2 = 4"
        result.tools_used  # ["calculator"]
        result.iterations  # 2
        ```
        """
        self.logger.agent.final_answer(response.content or "")
        return AgentResponse(
            answer=response.content or "",
            tools_used=tools_used,
            iterations=iterations,
        )
