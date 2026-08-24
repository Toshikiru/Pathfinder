"""
Checkpoint 2, Deliverable 8 - Vector Database Setup
Chunks every processed document (all 30, not just the Checkpoint 1 sample),
embeds each chunk with sentence-transformers/all-MiniLM-L6-v2, and loads
them into a persistent Chroma collection with cosine similarity search.

Chroma is configured with hnsw:space="cosine" (see docs/Distance_Metric_Comparison.md
for why cosine was chosen over Euclidean/dot product for this corpus).

Run directly to (re)build the index and print a few similarity-search
results. Other scripts import `get_collection()` / `query()` to reuse the
same index instead of rebuilding it.
"""

from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
CHROMA_DIR = ROOT / "data" / "chroma_db"
COLLECTION_NAME = "pathfinder_bsis_advisor"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    """Same paragraph-aware chunking used in the Checkpoint 1 embedding demo,
    now applied corpus-wide instead of to a 5-document sample."""
    lines = [l for l in text.split("\n") if l.strip()]
    chunks, current, current_len = [], [], 0
    for line in lines:
        if current_len + len(line) > max_chars and current:
            chunks.append("\n".join(current))
            current, current_len = [], 0
        current.append(line)
        current_len += len(line)
    if current:
        chunks.append("\n".join(current))
    return chunks


def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)


def build_index() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = get_embedding_function()

    # Rebuild clean each time so the index always matches the current corpus.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    ids, docs, metadatas = [], [], []
    doc_paths = sorted(p for p in PROCESSED_DIR.rglob("*.txt") if p.name != "_manifest.json")
    for path in doc_paths:
        rel = str(path.relative_to(PROCESSED_DIR)).replace("\\", "/")
        category = rel.split("/")[0]  # tpc_website | curriculum | policies
        text = path.read_text(encoding="utf-8")
        for i, chunk in enumerate(chunk_text(text)):
            ids.append(f"{rel}::chunk{i}")
            docs.append(chunk)
            metadatas.append({"source": rel, "category": category, "chunk_id": i})

    collection.add(ids=ids, documents=docs, metadatas=metadatas)
    print(f"Indexed {len(ids)} chunks from {len(doc_paths)} documents into '{COLLECTION_NAME}'.")
    return collection


def get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = get_embedding_function()
    return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)


def query(question: str, k: int = 4) -> list[dict]:
    collection = get_collection()
    result = collection.query(query_texts=[question], n_results=k)
    hits = []
    for doc, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        hits.append({"text": doc, "source": meta["source"], "distance": dist})
    return hits


DEMO_QUERIES = [
    "What are the prerequisites for Systems Analysis and Design?",
    "How many units can I enroll in while on academic probation?",
    "Who is the program head of BSIS?",
    "What is required to enroll in the Capstone Project?",
    "What is the GWA requirement for Latin honors?",
]

if __name__ == "__main__":
    build_index()
    print("\n" + "=" * 90)
    print("SIMILARITY SEARCH DEMO (cosine distance - lower is more similar)")
    print("=" * 90)
    for q in DEMO_QUERIES:
        hits = query(q, k=3)
        print(f"\nQuery: {q}")
        for rank, hit in enumerate(hits, 1):
            preview = hit["text"][:140].replace("\n", " ")
            print(f"  {rank}. [{hit['distance']:.4f}] {hit['source']}")
            print(f"     \"{preview}...\"")
