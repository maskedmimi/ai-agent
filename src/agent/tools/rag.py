"""
src/agent/tools/rag.py

A retrieval tool over Remy's own CV, backed by a local Chroma vector
store built by scripts/build_resume_index.py.

Design note: this tool only retrieves — it does NOT call the LLM to
generate an answer. It returns the most relevant raw chunks as text,
and lets the main agent's LLM compose the final natural-language
answer from them. This mirrors the existing tools in this project:
deterministic logic in the tool, reasoning left to the agent's LLM.
"""

from pathlib import Path

from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = Path("data/resume_index")
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 4  # how many chunks to retrieve per query

_vectorstore = None  # lazy-loaded, module-level cache (same pattern as DATAFRAME_CACHE)


def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        if not PERSIST_DIR.exists():
            raise FileNotFoundError(
                f"No resume index found at {PERSIST_DIR}. "
                "Run scripts/build_resume_index.py first."
            )
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        _vectorstore = Chroma(
            persist_directory=str(PERSIST_DIR),
            embedding_function=embeddings,
        )
    return _vectorstore


@tool
def search_resume(query: str) -> str:
    """
    Search Remy's CV for information relevant to the query.

    Use this tool when the user asks something about Remy's professional
    background, skills, work experience, education, or personal projects
    (e.g. "What AI projects has Remy built?" or "Where did Remy study?").

    Args:
        query (str): The natural-language question to search the CV for.

    Returns:
        str: The most relevant excerpts from the CV, concatenated. If
        nothing relevant is found, a message saying so is returned instead.
    """
    store = _get_vectorstore()
    results = store.similarity_search(query, k=TOP_K)

    if not results:
        return "No relevant information found in the CV for this query."

    excerpts = [f"[Excerpt {i+1}]\n{doc.page_content}" for i, doc in enumerate(results)]
    return "\n\n".join(excerpts)


TOOLS = [search_resume]
