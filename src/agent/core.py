"""Agent construction and invocation."""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from .config import MODEL_NAME, SYSTEM_PROMPT
from .tools.basics import TOOLS as BASIC_TOOLS
from .tools.math_ops import TOOLS as MATH_TOOLS
from .tools.rag import TOOLS as RAG_TOOLS

# As you add more tool files (e.g. tools/math_ops.py, tools/data_science.py),
# import their TOOLS list here and append to ALL_TOOLS.
ALL_TOOLS = [*BASIC_TOOLS, *MATH_TOOLS, *RAG_TOOLS]


def build_agent(model_name: str = MODEL_NAME, tools: list | None = None, system_prompt: str | None = None):
    """Create a local, tool-calling agent (Ollama-backed, no API key).

    Defaults to the generic personal-agent tool set and system prompt, so
    existing callers (chat.py, run_demo.py) are unaffected. Pass `tools=` /
    `system_prompt=` to build a differently-scoped agent (e.g. the Toyota
    voice assistant) without touching this function's defaults.
    """
    # qwen3 is a "thinking" model: by default it emits a full <think>...</think>
    # reasoning block before every answer (and again on every tool round-trip),
    # which is most of why responses feel slow. reasoning=False turns that off.
    llm = ChatOllama(model=model_name, reasoning=False)
    return create_agent(
        model=llm,
        tools=tools if tools is not None else ALL_TOOLS,
        system_prompt=system_prompt if system_prompt is not None else SYSTEM_PROMPT,
    )


def ask(agent, question: str) -> str:
    """Send a question to the agent and return its final text answer."""
    result = agent.invoke({"messages": [("human", question)]})
    return result["messages"][-1].content
