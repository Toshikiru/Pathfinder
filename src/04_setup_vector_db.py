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

import re
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
CHROMA_DIR = ROOT / "data" / "chroma_db"
COLLECTION_NAME = "pathfinder_bsis_advisor"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
TERM_FILENAME_RE = re.compile(r"year_(\d)_(first|second)_semester")


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    """Sentence-aware chunking used corpus-wide (same approach as the
    Checkpoint 1 embedding demo). Joins wrapped lines back into sentences,
    then groups whole sentences into chunks up to max_chars - never splits a
    sentence across two chunks (the earlier line/char-count version did,
    e.g. separating "...Latin honors" from "eligibility requires a GWA of
    1.75..." into different chunks, which degraded retrieval accuracy)."""
    joined = " ".join(l.strip() for l in text.split("\n") if l.strip())
    sentences = [s.strip() for s in SENTENCE_END.split(joined) if s.strip()]
    chunks, current, current_len = [], [], 0
    for sent in sentences:
        if current_len + len(sent) > max_chars and current:
            chunks.append(" ".join(current))
            current, current_len = [], 0
        current.append(sent)
        current_len += len(sent) + 1
    if current:
        chunks.append(" ".join(current))
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

        # Term-checklist files (curriculum/0N_year_Y_first|second_semester.txt)
        # all share near-identical header/table boilerplate ("BSIS Curriculum
        # Checklist - Year X - ... Semester, Program: Bachelor of Science in
        # Information Systems..."), so dense embedding similarity alone often
        # can't reliably tell "Year 1 Sem 1" apart from "Year 3 Sem 2" for a
        # generic phrasing like "first year first sem" - the distinguishing
        # tokens are a tiny fraction of the chunk. Tagging year/semester as
        # structured metadata lets the app filter directly instead of relying
        # on that fuzzy signal (see src/08_rag_app.py's detect_term()).
        term_match = TERM_FILENAME_RE.search(path.stem)
        year = int(term_match.group(1)) if term_match else None
        semester = ({"first": 1, "second": 2}[term_match.group(2)] if term_match else None)

        for i, chunk in enumerate(chunk_text(text)):
            ids.append(f"{rel}::chunk{i}")
            docs.append(chunk)
            metadata = {"source": rel, "category": category, "chunk_id": i}
            if year is not None:
                metadata["year"] = year
                metadata["semester"] = semester
            metadatas.append(metadata)

    collection.add(ids=ids, documents=docs, metadatas=metadatas)
    print(f"Indexed {len(ids)} chunks from {len(doc_paths)} documents into '{COLLECTION_NAME}'.")
    return collection


def get_collection() -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = get_embedding_function()
    return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)


def query(question: str, k: int = 4, where: dict | None = None) -> list[dict]:
    collection = get_collection()
    kwargs = {"query_texts": [question], "n_results": k}
    if where:
        kwargs["where"] = where
    result = collection.query(**kwargs)
    hits = []
    for doc, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
        hits.append({"text": doc, "source": meta["source"], "distance": dist})
    return hits


DEMO_QUERIES = [
    "What are the prerequisites for IS 104 System Analysis & Design?",
    "How many units can I enroll in while on academic probation?",
    "Who is the program head of BSIS?",
    "What is required to enroll in Capstone Project I?",
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
