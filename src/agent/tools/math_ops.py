"""Math tools for the agent."""

from langchain_core.tools import tool


@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a (a - b)."""
    return a - b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


@tool
def divide(a: float, b: float) -> float:
    """Divide a by b. Raises an error message if b is zero."""
    if b == 0:
        return "Error: division by zero is undefined."
    return a / b


TOOLS = [add, subtract, multiply, divide]
