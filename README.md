# AI Agent — Local, Tool-Calling LLM Agent

A tool-calling AI agent built from scratch with LangChain, running entirely on a
local LLM (Ollama + Qwen3) — no hosted API, no per-token cost. Built as a
hands-on portfolio project to learn agent architecture, tool calling, and
retrieval-augmented generation (RAG) from the ground up, rather than through
a single high-level framework call.

## Features

- **Multi-turn chat agent** with correctly preserved conversation history
  (native LangChain message objects, including `tool_call_id` linking between
  a tool call and its result — a non-obvious requirement covered below).
- **Custom tools**, each independently testable:
  - `math_ops` — add / subtract / multiply / divide, standard arithmetic
    (no sign-flipping tricks).
  - `basics` — small utility tools (e.g. current time, pre-formatted so the
    LLM isn't relied on to reformat raw values itself).
  - `rag` — retrieval-augmented tool that answers questions about my own CV,
    backed by a local vector store (see [RAG extension](#rag-extension)).
- **Fully local inference**: LLM (Qwen3:8b) and embeddings (`nomic-embed-text`)
  both run through Ollama — nothing leaves the machine, zero API cost.

## Architecture

```
User message
    │
    ▼
Agent (LangChain, Qwen3:8b via Ollama)
    │
    ├── decides: answer directly, or call a tool?
    │
    ▼
Tool call (math_ops / basics / rag)
    │
    ▼
Tool result → fed back into the agent as a ToolMessage
    │
    ▼
Agent composes the final natural-language answer
```

The design principle throughout: **tools do deterministic work, the LLM does
reasoning and language**. Anything that can be computed or looked up in code
(arithmetic, formatting, retrieval) is handled by a tool — the LLM is never
trusted to get that right on its own.

## Project structure

```
ai-agent/
├── src/
│   ├── agent/
│   │   ├── config.py          # MODEL_NAME, SYSTEM_PROMPT, TOYOTA_SYSTEM_PROMPT
│   │   ├── core.py             # build_agent(tools=, system_prompt=) — aggregates ALL_TOOLS by default
│   │   └── tools/
│   │       ├── basics.py
│   │       ├── math_ops.py
│   │       ├── rag.py           # search_resume tool (RAG over my CV)
│   │       ├── appointments.py  # Toyota demo: check_availability, book_appointment
│   │       ├── faq.py           # Toyota demo: search_warranty_faq (RAG)
│   │       └── handover.py      # Toyota demo: transfer_to_human
│   └── voice/
│       ├── stt.py               # faster-whisper wrapper
│       └── tts.py               # Piper wrapper
├── scripts/
│   ├── chat.py                     # interactive multi-turn CLI chat (generic agent)
│   ├── chat_toyota.py               # same, scoped to the Toyota persona (text-only)
│   ├── voice_app.py                 # Gradio push-to-talk interface (Toyota persona)
│   ├── run_demo.py                 # scripted, non-interactive demo
│   ├── build_resume_index.py       # one-off: builds the CV vector index
│   └── build_faq_index.py          # one-off: builds the FAQ vector index
├── data/
│   ├── resume_index/         # persisted Chroma vector store (gitignored)
│   ├── faq_index/            # persisted Chroma vector store, FAQ (gitignored)
│   ├── faq/                  # fictional warranty/maintenance FAQ source docs
│   ├── voices/               # Piper voice model (gitignored, re-downloadable)
│   └── appointments.db       # SQLite RDV store (gitignored)
├── docs/
│   └── plan_toyota_voice_assistant.md
├── tests/scenarios/          # V&V scenarios for the Toyota persona
├── requirements.txt
└── README.md
```

## Setup

**Prerequisites**
- [Ollama](https://ollama.com) installed and running
- Python 3.12+, WSL2 recommended if on Windows (see note below)

```bash
# Pull the models this project uses
ollama pull qwen3:8b
ollama pull nomic-embed-text

# Set up the environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

If running under WSL2 with Ollama installed natively on Windows, enable
mirrored networking so WSL can reach `localhost:11434`:

```ini
# %USERPROFILE%\.wslconfig
[wsl2]
networkingMode=mirrored
```
then `wsl --shutdown` and reopen your terminal.

## Usage

```bash
python scripts/chat.py
```

Then just chat — e.g. `"Add 18 and 19, then multiply by 4"` or (once the RAG
index is built) `"What AI projects has Remy worked on?"`.

## RAG extension

The `rag` tool adds retrieval over my own CV so the agent can answer questions
about my background:

1. `scripts/build_resume_index.py` loads the CV, splits it into overlapping
   chunks, embeds them locally (`nomic-embed-text` via Ollama), and persists
   them to a local Chroma vector store.
2. `src/agent/tools/rag.py` exposes a `search_resume` tool: given a query, it
   retrieves the most relevant chunks from that store and hands them back to
   the agent's LLM, which composes the actual answer.

Run the indexer once (and again whenever the CV changes):
```bash
python scripts/build_resume_index.py
```

**Note on the data source:** a first attempt used a visually-designed CV PDF
export, which turned out to have no real extractable text layer (the text was
rendered as vector shapes rather than stored as text) — `pypdf` silently
returned 0 characters. Switched to an older, text-based CV export, which
resolved it. Worth knowing if you're indexing a resume built with a
design-heavy export tool.

## Bugs found & fixed along the way

Documenting these because tracing *why* something broke is most of the
learning value of a project like this:

| Bug | Cause | Fix |
|---|---|---|
| `KeyError: 'tool_call_id'` on 2nd chat turn | Chat history rebuilt as plain tuples, losing `ToolMessage` metadata | Keep native LangChain message objects in history, don't convert them |
| Agent misreported a time value | LLM reformatted a raw value itself instead of using a deterministic tool output | Tool returns a pre-formatted string; LLM never reformats it |
| RAG indexing crashed with `Expected Embeddings to be non-empty` | PDF had 0 extractable characters (design-tool export, no real text layer) | Switched to a text-based CV export; added an explicit check that fails loudly instead of silently producing 0 chunks |
| RAG returned stale/wrong results after re-indexing | Chroma's `persist_directory` isn't cleared automatically between runs | `rm -rf data/resume_index` before rebuilding with a new source file |
| "Skills" section not retrieved | Small document + low `TOP_K` meant relevant chunks could be excluded | Increased `TOP_K`; confirmed content directly via `store.get()` rather than assuming |

## Toyota after-sales voice assistant (demo)

A second agent persona, built on the same `core.build_agent()` mechanism
but with its own restricted tool set and system prompt — a local,
from-scratch reconstruction of what a platform like Cognigy provides,
for an AYES/Toyota Motor Europe interview pitch. See
`docs/plan_toyota_voice_assistant.md` for the full design and build log.

- **Tools**: `check_availability` / `book_appointment` (SQLite-backed,
  with a deterministic `confirme` gate — see below), `search_warranty_faq`
  (RAG over a fictional FAQ), `transfer_to_human`.
- **Voice**: `faster-whisper` (STT, French) → agent → Piper (TTS, French),
  wired together in a push-to-talk Gradio interface.
- **Text-only testing**: `scripts/chat_toyota.py` runs the same agent at
  the keyboard, to validate the business logic before adding voice.

```bash
# One-time setup
python -m piper.download_voices --download-dir data/voices fr_FR-siwis-medium
python scripts/build_faq_index.py

# Test the business logic in text
python scripts/chat_toyota.py

# Full voice demo
python scripts/voice_app.py
```

**Bug found while testing**: with `reasoning=False` (needed for usable
voice latency, see below), `qwen3:8b` would sometimes call
`book_appointment` *before* asking the customer to confirm, and once even
claimed a booking succeeded after the tool had actually returned a
conflict error — i.e. it stopped reliably following the "confirm before
booking" instruction once its chain-of-thought was turned off. Fixed by
moving the gate into the tool itself: `book_appointment` takes a
`confirme: bool` argument and refuses to write to the database unless it's
`True`, returning a recap instead — so the ordering is enforced in
deterministic code, not left to prompt compliance. Same principle as the
rest of this project: the LLM proposes, the tool decides.

**Bug found while testing (stalling instead of acting)**: on a garbled
transcription ("Combien ne t'endure la garantie..." instead of "Combien de
temps dure..."), the agent would sometimes answer "Je vais vérifier, un
instant" and stop there — without ever calling `search_warranty_faq`. With
reasoning disabled, the model occasionally produces this kind of filler
response instead of either calling the tool or asking the customer to
repeat. Fixed by adding an explicit rule to the system prompt: never
announce an action without executing it in the same turn, and when input
is unclear, ask the customer to repeat rather than guessing or stalling.
Confirmed fixed on the same garbled input.

**Dependency bug found while testing**: `pip install faster-whisper` pulls
in the latest `av` (PyAV) by default, but `av>=19` removed the
`metadata_errors` kwarg that `faster-whisper==1.2.1`'s audio decoder
passes to `av.open()` — every transcription call crashed. Pinned
`av==13.1.0` in `requirements.txt`.

## Roadmap

- Discord bot integration
- Local image generation (Stable Diffusion / FLUX via ComfyUI)
- Expand the RAG source beyond a single CV file (project docs, notes) into a
  small local knowledge base

## Stack

Python · LangChain · Ollama (Qwen3:8b) · Chroma · `nomic-embed-text` ·
`faster-whisper` · Piper · Gradio · WSL2
