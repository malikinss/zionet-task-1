# ./src/tools/calculator.py

"""Safe arithmetic expression evaluator tool.

This module provides CalculatorTool, a BaseTool implementation that
parses and evaluates mathematical expressions using Python's AST module
without calling eval(), supporting basic arithmetic operators only.

Example:
    Basic usage:
    ```
    from src.tools.calculator import CalculatorTool

    tool = CalculatorTool()
    print(tool.run("2 + 2"))        # "2 + 2 = 4"
    print(tool.run("10 / 3"))       # "10 / 3 = 3.3333333333333335"
    print(tool.run("2 ** 8"))       # "2 ** 8 = 256"
    print(tool.run("10 / 0"))       # "Calculation error: division by zero"
    ```
"""

import ast
import operator
from src.tools.base import BaseTool
from src.tools.schema import ToolSchema, PropertySchema

from types import EllipsisType

ConstantValue = float | complex | str | bool | bytes | EllipsisType | None
"""Type alias for values that may appear as AST constants in expressions."""

ALLOWED_OPERATORS: dict = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
"""Mapping from AST operator node types to their callable equivalents.

Only operators present in this dict are permitted during evaluation.
Any other operator raises a `ValueError`.

Example:
```
op_fn = ALLOWED_OPERATORS[ast.Add]
op_fn(2, 3)  # 5
```
"""


class CalculatorTool(BaseTool):
    """A tool that safely evaluates arithmetic expressions via AST parsing.

    Parses expressions using Python's `ast` module and walks the
    resulting tree, permitting only the operators defined in
    `ALLOWED_OPERATORS`. No arbitrary code execution occurs.

    Example:
    ```
    tool = CalculatorTool()
    tool.run("3 * (4 + 2)")   # "3 * (4 + 2) = 18"
    tool.run("7 % 3")         # "7 % 3 = 1"
    tool.run("9 // 2")        # "9 // 2 = 4"
    ```
    """

    @property
    def name(self) -> str:
        """Returns the tool identifier used in LLM function calls.

        Returns:
            The string `"calculator"`.

        Example:
        ```
        tool.name  # "calculator"
        ```
        """
        return "calculator"

    @property
    def description(self) -> str:
        """Returns a short description of the tool for the LLM.

        Returns:
            A plain-text description of the tool's purpose.

        Example:
        ```
        tool.description  # "Safely evaluate a math expression"
        ```
        """
        return "Safely evaluate a math expression"

    @property
    def parameters(self) -> ToolSchema:
        """Returns the parameter schema expected by this tool.

        Returns:
            A ToolSchema requiring a single string property `expr`.

        Example:
        ```
        tool.parameters.properties
        # {"expr": PropertySchema(type="string")}
        ```
        """
        return ToolSchema(
            type="object",
            properties={"expr": PropertySchema(type="string")},
            required=["expr"],
        )

    def run(self, expr: str) -> str:
        """Parses and evaluates an arithmetic expression string.

        Parses `expr` into an AST, evaluates it via `_safe_eval`,
        and returns a formatted result string. Returns an error message
        instead of raising if evaluation fails.

        Args:
            expr: A string containing a valid arithmetic expression,
                e.g. `"2 + 2"` or `"10 / (3 - 1)"`.

        Returns:
            A string of the form `"<expr> = <result>"` on success,
            or `"Calculation error: <reason>"` on failure.

        Example:
        ```
        tool.run("3 + 4 * 2")   # "3 + 4 * 2 = 11"
        tool.run("1 / 0")       # "Calculation error: division by zero"
        tool.run("x + 1")       # "Calculation error: ..."
        ```
        """
        try:
            result = self._safe_eval(ast.parse(expr, mode="eval").body)
            return f"{expr} = {result}"
        except (ValueError, TypeError, ZeroDivisionError) as e:
            return f"Calculation error: {e}"

    def _safe_eval(self, node: ast.expr) -> ConstantValue:
        """Recursively evaluates an AST expression node.

        Returns the value of a constant node directly, or delegates
        to `_process_operation` for binary and unary operations.

        Args:
            node: An AST expression node to evaluate.

        Returns:
            The computed value of the node.

        Raises:
            ValueError: If the node type is not a constant, `BinOp`,
                or `UnaryOp`.

        Example:
        ```
        import ast
        node = ast.parse("3 + 4", mode="eval").body
        tool._safe_eval(node)  # 7
        ```
        """
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, (ast.BinOp, ast.UnaryOp)):
            return self._process_operation(node)
        raise ValueError(f"Unsupported expression: {node}")

    def _validate_operator(self, op):
        """Raises `ValueError` if the operator is not in `ALLOWED_OPERATORS`.

        Args:
            op: An AST operator node instance to validate.

        Raises:
            ValueError: If `type(op)` is not a key in `ALLOWED_OPERATORS`.

        Example:
        ```
        tool._validate_operator(ast.Add())    # passes
        tool._validate_operator(ast.BitAnd()) # raises ValueError
        ```
        """
        if type(op) not in ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported operator: {op}")

    def _process_operation(
        self, node: ast.BinOp | ast.UnaryOp
    ) -> ConstantValue:
        """Evaluates a binary or unary operation node.

        Validates the operator, resolves it from `ALLOWED_OPERATORS`,
        and recursively evaluates the operands.

        Args:
            node: An AST `BinOp` or `UnaryOp` node to evaluate.

        Returns:
            The computed result of the operation.

        Raises:
            ValueError: If the operator is not allowed or the node
                type is unsupported.

        Example:
        ```
        import ast
        node = ast.parse("-5", mode="eval").body
        tool._process_operation(node)  # -5
        ```
        """
        self._validate_operator(node.op)
        op = ALLOWED_OPERATORS[type(node.op)]

        if isinstance(node, ast.BinOp):
            return op(self._safe_eval(node.left), self._safe_eval(node.right))

        if isinstance(node, ast.UnaryOp):
            return op(self._safe_eval(node.operand))

        raise ValueError(f"Unsupported expression: {node}")
