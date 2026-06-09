# ./src/llm/dto.py

"""Data transfer objects for LLM interactions.

This module defines dataclasses used to represent structured data
exchanged between the application and LLM APIs, including tool calls,
conversation history, and model responses.

Example:
    Building a conversation turn with a tool call result::

        entry = HistoryEntry(role="user", content="What is the weather?")
        result = ToolResult(
            role="tool",
            tool_call_id="call_123",
            name="get_weather",
            content='{"temp": 22}'
        )
        print(entry.to_dict())
        print(result.to_dict())
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolCall:
    """Represents a single tool call requested by the LLM.

    Attributes:
        id: Unique identifier for the tool call.
        name: Name of the tool to invoke.
        args: Keyword arguments to pass to the tool.

    Example:
    ```
        tc = ToolCall(id="call_1", name="search", args={"query": "python"})
        print(tc.to_dict())
        # {"id": "call_1", "name": "search", "args": {"query": "python"}}
    ```
    """

    id: str
    name: str
    args: dict

    def to_dict(self) -> dict:
        """Serializes the tool call to a dictionary.

        Returns:
            A dict with keys `id`, `name`, and `args`.

        Example:
        ```
            tc = ToolCall(id="call_1", name="search", args={"query": "python"})
            tc.to_dict()
            # {"id": "call_1", "name": "search", "args": {"query": "python"}}
        ```
        """
        return {
            "id": self.id,
            "name": self.name,
            "args": self.args
        }


@dataclass
class FunctionInfo:
    """Describes a function invocation as represented in LLM API messages.

    Attributes:
        name: Name of the function being called.
        arguments: JSON-encoded string of the function arguments.

    Example:
    ```
        fi = FunctionInfo(name="get_weather", arguments='{"city": "Berlin"}')
        print(fi.to_dict())
        # {"name": "get_weather", "arguments": '{"city": "Berlin"}'}
    ```
    """

    name: str
    arguments: str

    def to_dict(self) -> dict:
        """Serializes the function info to a dictionary.

        Returns:
            A dict with keys `name` and `arguments`.

        Example:
        ```
            fi = FunctionInfo(
                name="get_weather", arguments='{"city": "Berlin"}'
            )
            fi.to_dict()
            # {"name": "get_weather", "arguments": '{"city": "Berlin"}'}
        ```
        """
        return {
            "name": self.name,
            "arguments": self.arguments
        }


@dataclass
class ToolCallEntry:
    """Represents a tool call entry in the format expected by LLM API messages.

    Attributes:
        id: Unique identifier for the tool call.
        type: Tool type identifier, typically `"function"`.
        function: Dictionary describing the function name and arguments.

    Example:
    ```
        entry = ToolCallEntry(
            id="call_42",
            type="function",
            function={"name": "get_weather", "arguments": '{"city": "Rome"}'}
        )
        print(entry.to_dict())
    ```
    """

    id: str
    type: str
    function: dict

    def to_dict(self) -> dict:
        """Serializes the tool call entry to a dictionary.

        Returns:
            A dict with keys `id`, `type`, and `function`.

        Example:
        ```
            entry = ToolCallEntry(
                id="call_42",
                type="function",
                function={
                    "name": "get_weather", "arguments": '{"city": "Rome"}'
                }
            )
            entry.to_dict()
            # {"id": "call_42", "type": "function", "function": {...}}
        ```
        """
        return {
            "id": self.id,
            "type": self.type,
            "function": self.function
        }


@dataclass
class HistoryEntry:
    """Represents a single message in a conversation history.

    Attributes:
        role: Speaker role, e.g. `"user"`, `"assistant"`, or `"system"`.
        content: Text content of the message.
        tool_calls: Optional list of tool calls attached to this message.

    Example:
    ```
        entry = HistoryEntry(role="user", content="What is 2 + 2?")
        print(entry.to_dict())
        # {"role": "user", "content": "What is 2 + 2?"}

        entry_with_tools = HistoryEntry(
            role="assistant",
            content="",
            tool_calls=[
                ToolCallEntry(id="c1", type="function", function={...})
            ]
        )
    ```
    """

    role: str
    content: str
    tool_calls: Optional[list[ToolCallEntry]] = None

    def to_dict(self) -> dict:
        """Serializes the history entry to a dictionary.

        Includes `tool_calls` only when it is not None.

        Returns:
            A dict with keys `role` and `content`, and optionally
            `tool_calls` as a list of serialized ToolCallEntry dicts.

        Example:
        ```
            entry = HistoryEntry(role="user", content="Hello")
            entry.to_dict()
            # {"role": "user", "content": "Hello"}
        ```
        """
        data: dict = {
            "role": self.role,
            "content": self.content,
        }
        if self.tool_calls is not None:
            data["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        return data


@dataclass
class ToolResult:
    """Represents the result returned from a tool invocation.

    Attributes:
        role: Message role, typically `"tool"`.
        tool_call_id: ID of the tool call this result corresponds to.
        name: Name of the tool that produced the result.
        content: String-encoded output of the tool.

    Example:
    ```
        result = ToolResult(
            role="tool",
            tool_call_id="call_1",
            name="search",
            content='["result1", "result2"]'
        )
        print(result.to_dict())
    ```
    """

    role: str
    tool_call_id: str
    name: str
    content: str

    def to_dict(self) -> dict:
        """Serializes the tool result to a dictionary.

        Returns:
            A dict with keys `role`, `tool_call_id`, `name`,
            and `content`.

        Example:
        ```
            result = ToolResult(
                role="tool",
                tool_call_id="call_1",
                name="search",
                content='["result1", "result2"]'
            )
            result.to_dict()
            # {"role": "tool", "tool_call_id": "call_1", ...}
        ```
        """
        return {
            "role": self.role,
            "tool_call_id": self.tool_call_id,
            "name": self.name,
            "content": self.content
        }


@dataclass
class LLMResponse:
    """Represents a response received from the LLM.

    Attributes:
        content: Text content of the response, or `None` if the model
            returned only tool calls.
        tool_calls: List of tool calls requested by the model.

    Example:
    ```
        response = LLMResponse(content="Hello!", tool_calls=[])
        print(response.has_tool_calls)  # False

        response_with_tools = LLMResponse(
            content=None,
            tool_calls=[
                ToolCall(id="c1", name="search", args={"query": "AI"})
            ]
        )
        print(response_with_tools.has_tool_calls)  # True
    ```
    """

    content: Optional[str]
    tool_calls: list[ToolCall]

    @property
    def has_tool_calls(self) -> bool:
        """Indicates whether the response contains any tool calls.

        Returns:
            `True` if the tool_calls list is non-empty, `False` otherwise.

        Example:
        ```
            LLMResponse(content="Hi", tool_calls=[]).has_tool_calls
            # False
            LLMResponse(
                content=None, tool_calls=[ToolCall(...)]
            ).has_tool_calls
            # True
        ```
        """
        return len(self.tool_calls) > 0
