"""
scripts/build_faq_index.py

One-off indexing script: reads the (fictional) warranty/maintenance FAQ
documents from data/faq/, splits them into chunks, embeds them locally via
Ollama, and persists them to a local Chroma vector store on disk.

Mirrors scripts/build_resume_index.py, but over data/faq/*.md instead of a
single CV PDF.

Run this once (and again any time a FAQ file changes):
    python scripts/build_faq_index.py
"""

from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# ---- Config -----------------------------------------------------------
FAQ_DIR = Path("data/faq")
PERSIST_DIR = Path("data/faq_index")
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
# ------------------------------------------------------------------------


def main() -> None:
    faq_files = sorted(FAQ_DIR.glob("*.md"))
    if not faq_files:
        raise FileNotFoundError(
            f"No FAQ files found in {FAQ_DIR}. Add at least one .md file first."
        )

    print(f"[1/4] Loading {len(faq_files)} FAQ file(s) from {FAQ_DIR} ...")
    pages = []
    for path in faq_files:
        pages.extend(TextLoader(str(path), encoding="utf-8").load())
    print(f"      -> loaded {len(pages)} document(s)")

    print("[2/4] Splitting into chunks ...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(pages)
    if not chunks:
        raise ValueError("FAQ files produced 0 chunks — check they aren't empty.")
    print(f"      -> {len(chunks)} chunk(s)")

    print(f"[3/4] Embedding chunks locally with '{EMBEDDING_MODEL}' via Ollama ...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    print(f"[4/4] Writing vector store to {PERSIST_DIR} ...")
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR),
    )

    print("Done. The FAQ index is ready to be queried by the search_warranty_faq tool.")


if __name__ == "__main__":
    main()
