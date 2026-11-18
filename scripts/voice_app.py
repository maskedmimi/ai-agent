"""
scripts/voice_app.py

Gradio push-to-talk interface for the Toyota after-sales voice assistant:
microphone (browser-side, avoids WSL audio driver issues) -> faster-whisper
(STT) -> the Toyota agent -> Piper (TTS).

No end-of-speech detection / barge-in: the customer records, then clicks
"Envoyer" explicitly (push-to-talk), as specified in
docs/plan_toyota_voice_assistant.md.

Run with:
    python scripts/voice_app.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import gradio as gr
from langchain_core.messages import HumanMessage

from agent.core import build_agent
from agent.config import TOYOTA_SYSTEM_PROMPT
from agent.tools.appointments import TOOLS as APPOINTMENT_TOOLS
from agent.tools.faq import TOOLS as FAQ_TOOLS
from agent.tools.handover import TOOLS as HANDOVER_TOOLS
from voice import stt, tts

TOYOTA_TOOLS = [*APPOINTMENT_TOOLS, *FAQ_TOOLS, *HANDOVER_TOOLS]

# Built once at startup — building the LangGraph agent is cheap; the
# expensive part (the qwen3:8b weights) stays loaded in Ollama across calls.
agent = build_agent(tools=TOYOTA_TOOLS, system_prompt=TOYOTA_SYSTEM_PROMPT)

_MARKDOWN_PATTERNS = [
    (re.compile(r"\*\*(.+?)\*\*"), r"\1"),  # **bold**
    (re.compile(r"\*(.+?)\*"), r"\1"),  # *italic*
    (re.compile(r"^[-*]\s+", flags=re.MULTILINE), ""),  # bullet lists
    (re.compile(r"^\d+\.\s+", flags=re.MULTILINE), ""),  # numbered lists
    (re.compile(r"`([^`]+)`"), r"\1"),  # `code`
]


def strip_markdown(text: str) -> str:
    """Remove common markdown so text reads naturally out loud via TTS."""
    for pattern, replacement in _MARKDOWN_PATTERNS:
        text = pattern.sub(replacement, text)
    return text.strip()


def handle_turn(audio_path, lc_history, chat_display):
    if audio_path is None:
        return chat_display, None, lc_history, None

    transcript = stt.transcribe(audio_path)
    if not transcript:
        chat_display = chat_display + [
            {"role": "assistant", "content": "Je n'ai rien entendu, pouvez-vous réessayer ?"}
        ]
        return chat_display, None, lc_history, None

    lc_history = lc_history + [HumanMessage(content=transcript)]
    result = agent.invoke({"messages": lc_history})
    lc_history = result["messages"]

    final_text = lc_history[-1].content
    clean_text = strip_markdown(final_text)
    audio_out_path = tts.synthesize(clean_text)

    chat_display = chat_display + [
        {"role": "user", "content": transcript},
        {"role": "assistant", "content": clean_text},
    ]

    # Clear the mic input so the next recording starts fresh (push-to-talk).
    return chat_display, audio_out_path, lc_history, None


with gr.Blocks(title="Assistant après-vente Toyota") as demo:
    gr.Markdown(
        "# 🚗 Assistant vocal après-vente Toyota\n"
        "Enregistrez votre message puis cliquez sur **Envoyer** (push-to-talk)."
    )

    lc_history_state = gr.State([])  # native LangChain message objects

    # Gradio 6's Chatbot only supports the role/content dict format now
    # (the old `type=` kwarg was removed along with the "tuples" format).
    chatbot = gr.Chatbot(label="Conversation")
    audio_out = gr.Audio(label="Réponse de l'assistant", autoplay=True)

    audio_in = gr.Audio(sources=["microphone"], type="filepath", label="Votre message")
    send_btn = gr.Button("Envoyer", variant="primary")

    send_btn.click(
        fn=handle_turn,
        inputs=[audio_in, lc_history_state, chatbot],
        outputs=[chatbot, audio_out, lc_history_state, audio_in],
        api_name="envoyer",
        # Gradio's default event queue holds a long-lived SSE connection
        # open for the whole session. Under WSL2, that connection can get
        # silently dropped by the Windows<->WSL network translation (same
        # family of issue as the Ollama networking note in the README),
        # leaving clicks that never reach the server with no visible error.
        # queue=False makes this a plain request/response call instead.
        queue=False,
    )

if __name__ == "__main__":
    demo.launch()
