"""Manual smoke test / demo runner for the local agent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent.core import build_agent, ask

if __name__ == "__main__":
    agent = build_agent()
    print(ask(agent, "What's 47 plus 89? Also, what time is it right now?"))
