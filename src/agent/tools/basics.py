"""Basic utility tools."""

from datetime import datetime
from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """Return the current date and time in a human-readable format."""
    return datetime.now().strftime("%I:%M %p on %B %d, %Y")


TOOLS = [get_current_time]
