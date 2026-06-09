# ./src/llm/__init__.py

"""Public API for the LLM package.

This module re-exports all classes intended for use by other packages,
providing a single stable import point for LLM clients and DTOs.

Example:
    Importing from the package directly:
    ```
    from src.llm import GeminiClient, GroqClient, LLMResponse

    client = GeminiClient()
    response: LLMResponse = client.generate(history=[...], schema=[])
    ```
"""

from src.llm.base import BaseLLMClient
from src.llm.dto import (
    LLMResponse, ToolCall, ToolResult,
    HistoryEntry, ToolCallEntry, FunctionInfo
)
from src.llm.groq_client import GroqClient
from src.llm.gemini_client import GeminiClient

__all__ = [
    "BaseLLMClient",
    "LLMResponse",
    "ToolCall",
    "ToolResult",
    "HistoryEntry",
    "ToolCallEntry",
    "FunctionInfo",
    "GroqClient",
    "GeminiClient",
]
