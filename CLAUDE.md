# AI Agent Project

Local, zero-API-cost tool-calling agent built with LangChain + LangGraph,
running on Ollama (Qwen3 8B) via WSL2. Goal: extensible personal agent for
tools like data analysis, Discord bot integration, and eventually
image/video generation — used as an interview demo project.

## Stack
- Model: Ollama, qwen3:8b (local, no API key)
- Framework: langchain.agents.create_agent (LangGraph under the hood)
- Env: WSL2 Ubuntu, Python venv at ./venv

## Conventions
- Tools live in src/agent/tools/, one file per logical group (e.g. basics.py, math.py)
- Every tool is a @tool-decorated function with a clear docstring (the LLM reads it)
- Agent construction logic lives in src/agent/core.py
- One-off manual test scripts go in scripts/, not mixed into src/

## Status
- [x] Ollama running locally, reachable from WSL
- [x] Basic tool-calling confirmed working (get_current_time, add)
- [ ] Real tool set not yet built
- [ ] Discord bot integration not started
