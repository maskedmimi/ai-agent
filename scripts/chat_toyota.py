"""
Interactive text chat with the Toyota after-sales voice assistant persona
— same loop as chat.py, but scoped to the appointment/FAQ/handover tools
and the Toyota system prompt, so the business logic can be validated at
the keyboard before the voice layer (STT/TTS/Gradio) is wired in.

See CLAUDE.md and docs/plan_toyota_voice_assistant.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langchain_core.messages import HumanMessage
from agent.core import build_agent
from agent.config import TOYOTA_SYSTEM_PROMPT
from agent.tools.appointments import TOOLS as APPOINTMENT_TOOLS
from agent.tools.faq import TOOLS as FAQ_TOOLS
from agent.tools.handover import TOOLS as HANDOVER_TOOLS

TOYOTA_TOOLS = [*APPOINTMENT_TOOLS, *FAQ_TOOLS, *HANDOVER_TOOLS]


def main():
    print("🚗 Assistant après-vente Toyota (texte) — tapez 'exit' ou 'quit' pour quitter\n")
    agent = build_agent(tools=TOYOTA_TOOLS, system_prompt=TOYOTA_SYSTEM_PROMPT)

    # Keep the actual message objects (not tuples) so ToolMessage /
    # AIMessage metadata like tool_call_id survives across turns.
    history = []

    while True:
        user_input = input("Client: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Au revoir !")
            break
        if not user_input:
            continue

        history.append(HumanMessage(content=user_input))

        result = agent.invoke({"messages": history})

        history = result["messages"]

        final_answer = history[-1].content
        print(f"Assistant: {final_answer}\n")


if __name__ == "__main__":
    main()
