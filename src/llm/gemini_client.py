# ./src/llm/gemini_client.py

"""Gemini LLM client implementation.

This module provides a concrete LLM client that communicates with
Google's Gemini API, handling content generation and tool call
parsing. Model name is configurable via the GEMINI_MODEL_NAME
environment variable.

Example:
    Basic usage with no tools::
        client = GeminiClient()
        response = client.generate(
            history=[{"role": "user", "parts": ["What is 2 + 2?"]}],
            schema=[]
        )
        print(response.content)  # "4"

    Usage with tools::
        schema = [{
            "name": "get_weather",
            "description": "Returns current weather for a city.",
            "parameters": {
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            }
        }]
        response = client.generate(history=history, schema=schema)
        if response.has_tool_calls:
            print(response.tool_calls[0].name)  # "get_weather"
"""

import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from src.llm.base import BaseLLMClient
from src.llm.dto import LLMResponse, ToolCall

load_dotenv()

DEFAULT_MODEL: str = "gemini-2.5-flash"
"""Fallback Gemini model name used when GEMINI_MODEL_NAME is not set."""

MODEL: str = os.getenv("GEMINI_MODEL_NAME", DEFAULT_MODEL)
"""Active Gemini model name, resolved from the environment at import time."""


class GeminiClient(BaseLLMClient):
    """LLM client that wraps the Google Gemini generative AI API.

    Translates the generic `history` and `schema` format used by
    BaseLLMClient into Gemini-specific API calls, and parses the
    response back into a unified LLMResponse DTO.

    Attributes:
        model: Name of the Gemini model to use for generation.
        client: Authenticated `genai.Client` instance.

    Example:
    ```
        client = GeminiClient(model="gemini-2.5-flash")
        response = client.generate(history=[...], schema=[])
        print(response.content)
    ```
    """

    def __init__(self, model: str = MODEL):
        """Initializes the Gemini client with an API key from the environment.

        Args:
            model: Gemini model name. Defaults to the module-level
                MODEL constant resolved from GEMINI_MODEL_NAME env var.

        Example:
        ```
            client = GeminiClient()
            client = GeminiClient(model="gemini-2.5-pro")
        ```
        """
        self.model = model
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def generate(self, history: list, schema: list[dict]) -> LLMResponse:
        """Sends a conversation history to Gemini and returns
        a parsed response.

        Builds a tool config from the provided schema, calls the Gemini
        API, and extracts either text content or tool calls from the
        first response candidate.

        Args:
            history: Conversation turns in Gemini-compatible format.
            schema: List of tool definitions, each containing `name`,
                `description`, and `parameters`.

        Returns:
            An LLMResponse with text content if the model replied in
            plain text, or a list of ToolCall objects if the model
            requested tool invocations.

        Example:
        ```
            response = client.generate(
                history=[{"role": "user", "parts": ["Hello"]}],
                schema=[]
            )
            print(response.content)   # "Hello! How can I help you?"
            print(response.tool_calls)  # []
        ```
        """
        response = self.client.models.generate_content(
            model=self.model,
            contents=history,
            config=types.GenerateContentConfig(
                tools=self._build_tools(schema)
            ),
        )
        candidates = response.candidates or []
        candidate_content = candidates[0].content
        parts = candidate_content.parts if candidate_content else []
        tool_calls = [
            ToolCall(
                id=str(p.function_call.name or ""),
                name=str(p.function_call.name or ""),
                args=dict(p.function_call.args or {}),
            )
            for p in (parts or [])
            if p.function_call is not None
        ]
        text = parts[0].text if not tool_calls and parts else None
        return LLMResponse(text, tool_calls)

    def _build_tools(self, schema: list[dict]) -> list:
        """Converts a list of tool definitions into a Gemini Tool object.

        Args:
            schema: List of tool dicts, each with `name`, `description`,
                and `parameters`.

        Returns:
            A single-element list containing a `types.Tool` with all
            function declarations derived from the schema.

        Example:
        ```
            tools = client._build_tools([{
                "name": "search",
                "description": "Searches the web.",
                "parameters": {
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"]
                }
            }])
        ```
        """
        return [
            types.Tool(
                function_declarations=[
                    self._declare_function_info(t) for t in schema
                ]
            )
        ]

    @staticmethod
    def _declare_function_info(t: dict) -> types.FunctionDeclaration:
        """Builds a Gemini FunctionDeclaration from a tool definition dict.

        Args:
            t: Tool definition dict with keys `name`, `description`,
                and `parameters`.

        Returns:
            A `types.FunctionDeclaration` ready to be passed to the API.

        Example:
        ```
            decl = GeminiClient._declare_function_info({
                "name": "get_weather",
                "description": "Returns weather data.",
                "parameters": {
                    "properties": {"city": {"type": "string"}},
                    "required": ["city"]
                }
            })
        ```
        """
        return types.FunctionDeclaration(
            name=t["name"],
            description=t["description"],
            parameters=GeminiClient._declare_parameters(t["parameters"]),
        )

    @staticmethod
    def _declare_parameters(parameters: dict) -> types.Schema:
        """Converts a JSON Schema parameters dict into a Gemini Schema object.

        Args:
            parameters: Dict with `properties` (required) and optionally
                `required` listing mandatory property names.

        Returns:
            A `types.Schema` of type OBJECT with declared properties
            and required fields.

        Example:
        ```
            schema = GeminiClient._declare_parameters({
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            })
        ```
        """
        return types.Schema(
            type=types.Type.OBJECT,
            properties=GeminiClient._declare_properties(
                parameters["properties"]
            ),
            required=parameters.get("required", []),
        )

    @staticmethod
    def _declare_properties(props: dict) -> dict[str, types.Schema]:
        """Converts a properties dict into a mapping of Gemini Schema objects.

        Args:
            props: Dict mapping property names to their type definitions,
                where each value contains at least a `type` key.

        Returns:
            A dict mapping each property name to a `types.Schema`
            with the corresponding uppercased type.

        Example:
        ```
            schemas = GeminiClient._declare_properties({
                "city": {"type": "string"},
                "units": {"type": "string"}
            })
            # {"city": Schema(type=STRING), "units": Schema(type=STRING)}
        ```
        """
        return {
            k: types.Schema(type=v["type"].upper())
            for k, v in props.items()
        }
