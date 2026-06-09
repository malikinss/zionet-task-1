# ./src/tools/__init__.py

"""Public API for the tools package.

This module re-exports the core classes intended for use by other
packages, providing a single stable import point for tool base
classes, schemas, and the registry.

Example:
    Importing from the package directly:
    ```
    from src.tools import BaseTool, ToolSchema, PropertySchema, ToolRegistry

    registry = ToolRegistry()
    schema = registry.to_tools_schema()
    ```
"""

from src.tools.base import BaseTool
from src.tools.schema import ToolSchema, PropertySchema
from src.tools.registry import ToolRegistry

__all__ = ["BaseTool", "ToolSchema", "PropertySchema", "ToolRegistry"]
