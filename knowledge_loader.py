"""
Knowledge loader – ingestion, chunking, and FAISS retrieval
===========================================================
Loads plain-text / markdown / PDF documents from the ``knowledge/``
directory tree, splits them into overlapping chunks, and builds (or
reloads) a FAISS index for semantic retrieval.

Dependencies (optional)
-----------------------
faiss-cpu  : vector search  – pip install faiss-cpu
numpy      : required by FAISS
pypdf      : PDF support     – pip install pypdf
openai     : embeddings      – pip install openai

When the optional packages are absent the loader still imports cleanly;
retrieval simply returns an empty list with a status flag.
"""

import os
import pickle
import re
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Optional dependency detection
# ---------------------------------------------------------------------------
try:
    import numpy as np
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    _FAISS_AVAILABLE = False

try:
    from pypdf import PdfReader
    _PYPDF_AVAILABLE = True
except ImportError:
    _PYPDF_AVAILABLE = False

# Default locations
KNOWLEDGE_DIR  = Path(__file__).parent / "knowledge"
INDEX_PATH     = Path(__file__).parent / "data" / "buddy_index.faiss"
CHUNKS_PATH    = Path(__file__).parent / "data" / "buddy_chunks.pkl"
EMBED_DIM      = 1536   # text-embedding-3-small output dimension
CHUNK_SIZE     = 600    # target characters per chunk
CHUNK_OVERLAP  = 100    # character overlap between consecutive chunks


# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _read_pdf_file(path: Path) -> str:
    if not _PYPDF_AVAILABLE:
        return ""
    try:
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        return ""


def _extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return _read_text_file(path)
    if suffix == ".pdf":
        return _read_pdf_file(path)
    return ""


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def _chunk_text(text: str, source: str) -> list[dict]:
    """Split *text* into overlapping chunks; return list of chunk dicts."""
    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []

    chunks = []
    start  = 0
    while start < len(text):
        end   = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append({"text": chunk, "source": source})
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# ---------------------------------------------------------------------------
# Embedding helper (uses llm_client's OpenAI credentials)
# ---------------------------------------------------------------------------

def _embed_texts(texts: list[str]) -> Optional[list]:
    """Return a list of embedding vectors (as lists of floats), or None on error."""
    import os
    try:
        import openai
    except ImportError:
        return None

    provider = os.environ.get("LLM_PROVIDER", "OPENAI").upper().strip()
    if provider == "AZURE_OPENAI":
        key      = os.environ.get("AZURE_OPENAI_KEY", "").strip()
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
        version  = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01")
        client   = openai.AzureOpenAI(api_key=key, azure_endpoint=endpoint,
                                       api_version=version)
        model    = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT",
                                   "text-embedding-3-small")
    else:
        key    = os.environ.get("OPENAI_API_KEY", "").strip()
        client = openai.OpenAI(api_key=key)
        model  = os.environ.get("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    batch_size = 100
    all_vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp  = client.embeddings.create(input=batch, model=model)
        all_vectors.extend([item.embedding for item in resp.data])
    return all_vectors


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_documents(knowledge_dir: Path = KNOWLEDGE_DIR) -> list[dict]:
    """Walk *knowledge_dir* and return a flat list of chunk dicts."""
    chunks = []
    if not knowledge_dir.exists():
        return chunks
    for path in sorted(knowledge_dir.rglob("*")):
        if path.is_file():
            text = _extract_text(path)
            if text.strip():
                rel = str(path.relative_to(knowledge_dir.parent))
                chunks.extend(_chunk_text(text, source=rel))
    return chunks


def build_index(
    chunks: list[dict],
    index_path: Path = INDEX_PATH,
    chunks_path: Path = CHUNKS_PATH,
) -> tuple[bool, str]:
    """
    Embed *chunks* and write a FAISS index + pickle file.

    Returns (success: bool, message: str).
    """
    if not _FAISS_AVAILABLE:
        return False, "faiss-cpu is not installed. Run: pip install faiss-cpu numpy"
    if not chunks:
        return False, "No document chunks to index."

    texts    = [c["text"] for c in chunks]
    vectors  = _embed_texts(texts)
    if vectors is None:
        return False, "Could not generate embeddings (openai package missing or key unset)."

    arr   = np.array(vectors, dtype="float32")
    dim   = arr.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(arr)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))
    with open(chunks_path, "wb") as fh:
        pickle.dump(chunks, fh)

    return True, f"Index built: {len(chunks)} chunks from {len(set(c['source'] for c in chunks))} files."


def load_index(
    index_path: Path = INDEX_PATH,
    chunks_path: Path = CHUNKS_PATH,
) -> tuple[Optional[object], Optional[list]]:
    """Load a previously built FAISS index. Returns (index, chunks) or (None, None)."""
    if not _FAISS_AVAILABLE:
        return None, None
    if not index_path.exists() or not chunks_path.exists():
        return None, None
    try:
        index = faiss.read_index(str(index_path))
        with open(chunks_path, "rb") as fh:
            chunks = pickle.load(fh)
        return index, chunks
    except Exception:
        return None, None


def retrieve(
    query: str,
    index,
    chunks: list[dict],
    top_k: int = 4,
) -> list[dict]:
    """
    Embed *query* and return the top-k most similar chunks.
    Returns an empty list if retrieval fails.
    """
    if not _FAISS_AVAILABLE or index is None:
        return []
    vecs = _embed_texts([query])
    if not vecs:
        return []
    arr = np.array(vecs, dtype="float32")
    _, indices = index.search(arr, top_k)
    return [chunks[i] for i in indices[0] if i < len(chunks)]


# ---------------------------------------------------------------------------
# CLI convenience: python knowledge_loader.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Loading documents from knowledge/ …")
    doc_chunks = load_documents()
    print(f"  Found {len(doc_chunks)} chunks.")
    if doc_chunks:
        ok, msg = build_index(doc_chunks)
        print("  " + msg)
    else:
        print("  No documents found. Add .md/.txt/.pdf files to the knowledge/ subfolders.")
