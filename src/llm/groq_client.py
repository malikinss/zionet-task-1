# ./src/llm/groq_client.py

"""Groq LLM client implementation.

This module provides a concrete LLM client that communicates with
the Groq API using OpenAI-compatible chat completions, handling
content generation and tool call parsing. Model name is configurable
via the `GROQ_MODEL_NAME` environment variable.

Example:
    Basic usage with no tools:
    ```
    client = GroqClient()
    response = client.generate(
        history=[{"role": "user", "content": "What is 2 + 2?"}],
        schema=[]
    )
    print(response.content)  # "4"
    ```

    Usage with tools:
    ```
    schema = [{
        "name": "get_weather",
        "description": "Returns current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }]
    response = client.generate(history=history, schema=schema)
    if response.has_tool_calls:
        print(response.tool_calls[0].name)  # "get_weather"
    ```
"""

import json
import os
from groq import Groq
from dotenv import load_dotenv
from src.llm.base import BaseLLMClient
from src.llm.dto import LLMResponse, ToolCall

load_dotenv()

DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
"""Fallback Groq model name used when `GROQ_MODEL_NAME` is not set."""

MODEL: str = os.getenv("GROQ_MODEL_NAME", DEFAULT_MODEL)
"""Active Groq model name, resolved from the environment at import time."""


class GroqClient(BaseLLMClient):
    """LLM client that wraps the Groq chat completions API.

    Translates the generic `history` and `schema` format used by
    `BaseLLMClient` into Groq-compatible API calls, and parses the
    response back into a unified `LLMResponse` DTO.

    Attributes:
        model: Name of the Groq model to use for generation.
        client: Authenticated `Groq` client instance.

    Example:
    ```
        client = GroqClient(model="llama3-groq-70b-8192-tool-use-preview")
        response = client.generate(history=[...], schema=[])
        print(response.content)
    ```
    """

    def __init__(self, model: str = MODEL):
        """Initializes the Groq client with an API key from the environment.

        Args:
            model: Groq model name. Defaults to the module-level MODEL
                constant resolved from GROQ_MODEL_NAME env var.

        Example:
        ```
            client = GroqClient()
            client = GroqClient(model="llama3-groq-8b-8192")
        ```
        """
        self.model = model
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def generate(self, history: list, schema: list[dict]) -> LLMResponse:
        """Sends a conversation history to Groq and returns a parsed response.

        Builds a tool list from the provided schema, calls the Groq chat
        completions API with `tool_choice="auto"`, and extracts either
        text content or tool calls from the first response choice.

        Args:
            history: Conversation turns as a list of OpenAI-compatible
                message dicts with `role` and `content` keys.
            schema: List of tool definitions, each containing `name`,
                `description`, and `parameters`.

        Returns:
            An LLMResponse with text content if the model replied in
            plain text, or a list of ToolCall objects if the model
            requested tool invocations.

        Example:
        ```
            response = client.generate(
                history=[{"role": "user", "content": "Hello"}],
                schema=[]
            )
            print(response.content)    # "Hello! How can I help you?"
            print(response.tool_calls) # []
        ```
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=history,
            tools=self._build_tools(schema),
            tool_choice="auto",
        )
        message = response.choices[0].message
        tool_calls = [
            ToolCall(
                id=tc.id,
                name=tc.function.name,
                args=self._get_args(tc),
            )
            for tc in (message.tool_calls or [])
        ]
        return LLMResponse(content=message.content, tool_calls=tool_calls)

    def _get_args(self, tc) -> dict:
        """Parses tool call arguments into a plain dictionary.

        Handles both pre-parsed dict arguments and JSON-encoded strings,
        which the Groq API may return depending on the model.

        Args:
            tc: A tool call object with a `function.arguments` attribute
                that is either a JSON string or a dict.

        Returns:
            A dict of the tool call arguments, or an empty dict if the
            arguments are missing or empty.

        Example:
        ```
            # When arguments arrive as a JSON string:
            tc.function.arguments = '{"city": "Berlin"}'
            client._get_args(tc)  # {"city": "Berlin"}

            # When arguments arrive already parsed:
            tc.function.arguments = {"city": "Berlin"}
            client._get_args(tc)  # {"city": "Berlin"}
        ```
        """
        args = tc.function.arguments
        if isinstance(args, str):
            return json.loads(args or "{}")
        return (args or {})

    @staticmethod
    def _declare_function_info(tool: dict) -> dict:
        """Extracts function metadata from a tool definition dict.

        Args:
            tool: Tool definition with keys `name`, `description`,
                and `parameters`.

        Returns:
            A dict with the same three keys, ready to be nested under
            the `"function"` key in a Groq tool entry.

        Example:
        ```
            GroqClient._declare_function_info({
                "name": "search",
                "description": "Searches the web.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"]
                }
            })
            '''
            {
                "name": "search",
                "description": "Searches the web.",
                "parameters": {...}
            }
            '''
        ```
        """
        return {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["parameters"]
        }

    def _build_tools(self, schema: list[dict]) -> list:
        """Converts a list of tool definitions into Groq-compatible tool dicts.

        Args:
            schema: List of tool definitions, each containing `name`,
                `description`, and `parameters`.

        Returns:
            A list of dicts with `type` set to `"function"` and a
            nested `function` key holding the declaration.

        Example:
        ```
            tools = client._build_tools([{
                "name": "search",
                "description": "Searches the web.",
                "parameters": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"]
                }
            }])
            # [{"type": "function", "function": {"name": "search", ...}}]
        ```
        """
        return [
            {
                "type": "function",
                "function": self._declare_function_info(tool)
            }
            for tool in schema
        ]
