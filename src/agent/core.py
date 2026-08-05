"""Agent construction and invocation."""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from .config import MODEL_NAME, SYSTEM_PROMPT
from .tools.basics import TOOLS as BASIC_TOOLS
from .tools.math_ops import TOOLS as MATH_TOOLS

# As you add more tool files (e.g. tools/math_ops.py, tools/data_science.py),
# import their TOOLS list here and append to ALL_TOOLS.
ALL_TOOLS = [*BASIC_TOOLS, *MATH_TOOLS]


def build_agent(model_name: str = MODEL_NAME):
    """Create the local, tool-calling agent (Ollama-backed, no API key)."""
    llm = ChatOllama(model=model_name)
    return create_agent(model=llm, tools=ALL_TOOLS, system_prompt=SYSTEM_PROMPT)


def ask(agent, question: str) -> str:
    """Send a question to the agent and return its final text answer."""
    result = agent.invoke({"messages": [("human", question)]})
    return result["messages"][-1].content
