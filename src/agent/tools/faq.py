"""
src/agent/tools/faq.py

A retrieval tool over the (fictional) Toyota warranty/maintenance FAQ,
backed by a local Chroma vector store built by scripts/build_faq_index.py.

Same design as src/agent/tools/rag.py: this tool only retrieves — it does
NOT call the LLM to generate an answer. It returns the most relevant raw
chunks as text, and lets the main agent's LLM compose the final
natural-language answer from them.
"""

from pathlib import Path

from langchain_core.tools import tool
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = Path("data/faq_index")
EMBEDDING_MODEL = "nomic-embed-text"
TOP_K = 4  # how many chunks to retrieve per query

_vectorstore = None  # lazy-loaded, module-level cache (same pattern as rag.py)


def _get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        if not PERSIST_DIR.exists():
            raise FileNotFoundError(
                f"No FAQ index found at {PERSIST_DIR}. "
                "Run scripts/build_faq_index.py first."
            )
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        _vectorstore = Chroma(
            persist_directory=str(PERSIST_DIR),
            embedding_function=embeddings,
        )
    return _vectorstore


@tool
def search_warranty_faq(question: str) -> str:
    """
    Search the dealership's warranty/maintenance FAQ for information
    relevant to the customer's question.

    Use this tool for any question about warranty coverage, maintenance
    schedules, or breakdown assistance (e.g. "Combien de temps dure la
    garantie ?" or "Quand faut-il changer le filtre à habitacle ?").

    Args:
        question (str): The customer's natural-language question.

    Returns:
        str: The most relevant FAQ excerpts, concatenated. If nothing
        relevant is found, a message saying so is returned instead — in
        that case, offer to transfer the customer to a human advisor
        rather than guessing.
    """
    store = _get_vectorstore()
    results = store.similarity_search(question, k=TOP_K)

    if not results:
        return "Aucune information pertinente trouvée dans la FAQ pour cette question."

    excerpts = [f"[Extrait {i+1}]\n{doc.page_content}" for i, doc in enumerate(results)]
    return "\n\n".join(excerpts)


TOOLS = [search_warranty_faq]
