from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

@tool
def get_current_time() -> str:
    """Return the current date and time in a human-readable format."""
    from datetime import datetime
    return datetime.now().strftime("%I:%M %p on %B %d, %Y")  # e.g. "09:28 PM on August 05, 2026"

@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

llm = ChatOllama(model="qwen3:8b")
agent = create_react_agent(model=llm, tools=[get_current_time, add])

response = agent.invoke({
    "messages": [("human", "What's 47 plus 89? Also, what time is it right now?")]
})

for msg in response["messages"]:
    print(f"[{type(msg).__name__}] {getattr(msg, 'content', '')}")
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        print(f"  → tool calls: {msg.tool_calls}")
