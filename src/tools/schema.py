# ./src/tools/schema.py

"""Schema dataclasses for tool parameter definitions.

This module defines lightweight dataclasses used to describe the
input parameters of tools in a structured, serializable format
compatible with LLM function-calling APIs.

Example:
    Defining a tool schema with required properties:
    ```
    from src.tools.schema import ToolSchema, PropertySchema

    schema = ToolSchema(
        type="object",
        properties={
            "city": PropertySchema(type="string"),
            "units": PropertySchema(type="string"),
        },
        required=["city"]
    )
    ```
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PropertySchema:
    """Describes the type of a single tool input property.

    Attributes:
        type: JSON Schema type string for the property,
            e.g. `"string"`, `"integer"`, `"boolean"`.

    Example:
    ```
    prop = PropertySchema(type="string")
    prop = PropertySchema(type="integer")
    ```
    """
    type: str


@dataclass
class ToolSchema:
    """Describes the full parameter schema for a tool.

    Attributes:
        type: JSON Schema type of the parameters object,
            typically `"object"`.
        properties: Mapping of parameter names to their PropertySchema.
        required: Optional list of parameter names that are mandatory.

    Example:
    ```
    schema = ToolSchema(
        type="object",
        properties={
            "query": PropertySchema(type="string"),
            "limit": PropertySchema(type="integer"),
        },
        required=["query"]
    )
    ```
    """
    type: str
    properties: dict[str, PropertySchema]
    required: Optional[list[str]] = None
