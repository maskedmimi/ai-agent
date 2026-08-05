"""Shared configuration for the agent."""

MODEL_NAME = "qwen3:8b"
SYSTEM_PROMPT = (
    "You are a helpful local AI assistant with access to tools. "
    "Use tools when they help answer the question accurately — "
    "don't guess at things a tool can compute or look up for you."
)
