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
├── src/agent/
│   ├── config.py            # MODEL_NAME, SYSTEM_PROMPT
│   ├── core.py               # build_agent(), ask() — aggregates all TOOLS
│   └── tools/
│       ├── basics.py
│       ├── math_ops.py
│       └── rag.py            # search_resume tool (RAG over my CV)
├── scripts/
│   ├── chat.py                     # interactive multi-turn CLI chat
│   ├── run_demo.py                 # scripted, non-interactive demo
│   └── build_resume_index.py       # one-off: builds the local vector index
├── data/
│   └── resume_index/         # persisted Chroma vector store (gitignored)
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

## Roadmap

- Discord bot integration
- Local image generation (Stable Diffusion / FLUX via ComfyUI)
- Expand the RAG source beyond a single CV file (project docs, notes) into a
  small local knowledge base

## Stack

Python · LangChain · Ollama (Qwen3:8b) · Chroma · `nomic-embed-text` · WSL2
