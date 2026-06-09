# ./src/llm/base.py

"""Base interface for LLM client implementations.

This module defines the abstract base class that all LLM client
implementations must inherit from, providing a consistent interface
for text generation and tool result construction.

Example:
    Implementing a custom LLM client::

        class MyLLMClient(BaseLLMClient):
            def generate(
                self, history: list, schema: list[dict]
            ) -> LLMResponse:
                ...
                return LLMResponse(content="Hello!", tool_calls=[])
"""

from abc import ABC, abstractmethod
from src.llm.dto import LLMResponse, ToolResult


class BaseLLMClient(ABC):
    """Abstract base class for LLM API clients.

    Subclasses must implement the `generate` method. The
    `build_tool_result` helper is provided as a concrete method
    shared across all implementations.

    Example:
    ```
        class OpenAIClient(BaseLLMClient):
            def generate(self, history, schema):
                ...
    ```
    """

    @abstractmethod
    def generate(self, history: list, schema: list[dict]) -> LLMResponse:
        """Sends a conversation history to the LLM and returns its response.

        Args:
            history: List of conversation messages. Each element is
                typically a dict or a DTO representing a single turn.
            schema: List of tool definitions in JSON Schema format
                describing the tools available to the model.

        Returns:
            An LLMResponse containing the model's text content and
            any tool calls it requested.

        Example:
        ```
            client = MyLLMClient()
            response = client.generate(
                history=[{"role": "user", "content": "What is 2 + 2?"}],
                schema=[]
            )
            print(response.content)  # "4"
        ```
        """
        pass

    def build_tool_result(
        self, tool_call_id: str, name: str, result: str
    ) -> ToolResult:
        """Constructs a ToolResult DTO from a tool invocation output.

        Args:
            tool_call_id: ID of the tool call this result corresponds to.
            name: Name of the tool that was invoked.
            result: String-encoded output returned by the tool.

        Returns:
            A ToolResult with role set to `"tool"` and the provided
            identifiers and content.

        Example:
        ```
            tool_result = client.build_tool_result(
                tool_call_id="call_1",
                name="search",
                result='["result1", "result2"]'
            )
            print(tool_result.role)  # "tool"
        ```
        """
        return ToolResult(
            role="tool",
            tool_call_id=tool_call_id,
            name=name,
            content=result,
        )
