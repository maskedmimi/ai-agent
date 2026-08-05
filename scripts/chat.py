"""Interactive chat loop with the local agent — similar to `ollama run`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.messages import HumanMessage
from agent.core import build_agent

def main():
    print("🤖 Local agent chat (type 'exit' or 'quit' to leave)\n")
    agent = build_agent()

    # Keep the actual message objects (not tuples) so ToolMessage /
    # AIMessage metadata like tool_call_id survives across turns.
    history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Bye!")
            break
        if not user_input:
            continue

        history.append(HumanMessage(content=user_input))

        result = agent.invoke({"messages": history})

        # result["messages"] is the full updated history as proper
        # message objects — just keep it as-is for the next turn.
        history = result["messages"]

        final_answer = history[-1].content
        print(f"Agent: {final_answer}\n")

if __name__ == "__main__":
    main()
