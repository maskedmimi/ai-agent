"""
scripts/build_resume_index.py

One-off indexing script: reads the CV PDF, splits it into chunks,
embeds those chunks locally via Ollama, and persists them to a local
Chroma vector store on disk.

Run this once (and again any time the CV changes):
    python scripts/build_resume_index.py

Prerequisites:
    pip install langchain-chroma chromadb pypdf langchain-text-splitters
    ollama pull nomic-embed-text
"""

from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

# ---- Config -----------------------------------------------------------
CV_PATH = Path("data/Remy_Chavrot_CV_0726.pdf")   # adjust to your real CV path
PERSIST_DIR = Path("data/resume_index")       # where Chroma stores its files
EMBEDDING_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 80      # overlap so facts near a chunk edge aren't lost
# ------------------------------------------------------------------------


def main() -> None:
    if not CV_PATH.exists():
        raise FileNotFoundError(
            f"CV not found at {CV_PATH}. Update CV_PATH at the top of this script."
        )

    print(f"[1/4] Loading {CV_PATH} ...")
    loader = PyPDFLoader(str(CV_PATH))
    pages = loader.load()
    print(f"      -> loaded {len(pages)} page(s)")

    print("[2/4] Splitting into chunks ...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(pages)
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

    print("Done. The resume index is ready to be queried by the search_resume tool.")


if __name__ == "__main__":
    main()
