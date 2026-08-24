"""
Stage 3 - Embedding Generation Demo
Converts a sample of the processed text into embeddings using an
open-source Hugging Face sentence-transformer model, and demonstrates that
semantically similar advising questions land close together in embedding
space (a sanity check before wiring up a real vector database in
Checkpoint 2).

Model choice: sentence-transformers/all-MiniLM-L6-v2
  - Open-source, runs fully locally/offline (satisfies CILO3's "open-source
    foundation model" requirement with zero API cost, which matters for a
    student project with no budget).
  - 384-dimensional embeddings: small enough to keep the future vector
    index fast and cheap to store for a 20-30 document corpus, while still
    scoring well on semantic-similarity benchmarks (MTEB) for short
    passages like ours (course descriptions, policy paragraphs).
  - Well-suited to short-to-medium text chunks (sentences/paragraphs),
    which matches how this corpus will be chunked for RAG in Checkpoint 3
    (per-course, per-policy-rule chunks rather than whole-document blobs).
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_DIR = ROOT / "data" / "processed" / "_embeddings"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# A handful of documents chosen to cover the three data categories
# (real scraped page, simulated curriculum, simulated policy).
SAMPLE_DOCS = [
    "tpc_website/academics_bachelor-of-science-in-information-systems.txt",
    "curriculum/05_year_3_first_semester.txt",
    "curriculum/course_descriptions_data_networks_security.txt",
    "policies/enrollment_prerequisites_and_academic_standing.txt",
    "policies/grading_system_and_gwa_policy.txt",
]

# Realistic advisor-bot queries used to sanity-check retrieval quality.
SAMPLE_QUERIES = [
    "What are the prerequisites for Systems Analysis and Design?",
    "How many units can I enroll in if I'm on academic probation?",
    "What courses cover database design?",
    "Who is the program head of BSIS?",
    "What GWA do I need for Latin honors?",
]


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
    """Simple paragraph-aware chunking: group lines until max_chars, break on blank-ish gaps."""
    lines = [l for l in text.split("\n") if l.strip()]
    chunks, current = [], []
    current_len = 0
    for line in lines:
        if current_len + len(line) > max_chars and current:
            chunks.append("\n".join(current))
            current, current_len = [], 0
        current.append(line)
        current_len += len(line)
    if current:
        chunks.append("\n".join(current))
    return chunks


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Loading model: {MODEL_NAME} ...")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Embedding dimension: {model.get_embedding_dimension()}")

    all_chunks: list[dict] = []
    for rel_path in SAMPLE_DOCS:
        path = PROCESSED_DIR / rel_path
        text = path.read_text(encoding="utf-8")
        for i, chunk in enumerate(chunk_text(text)):
            all_chunks.append({"source": rel_path, "chunk_id": i, "text": chunk})

    print(f"\nChunked {len(SAMPLE_DOCS)} sample documents into {len(all_chunks)} chunks.")
    chunk_texts = [c["text"] for c in all_chunks]
    chunk_embeddings = model.encode(chunk_texts, normalize_embeddings=True, show_progress_bar=False)

    query_embeddings = model.encode(SAMPLE_QUERIES, normalize_embeddings=True, show_progress_bar=False)

    print("\n" + "=" * 90)
    print("RETRIEVAL SANITY CHECK (cosine similarity, no vector DB yet - that's Checkpoint 2)")
    print("=" * 90)
    for query, qvec in zip(SAMPLE_QUERIES, query_embeddings):
        sims = chunk_embeddings @ qvec  # cosine sim since vectors are normalized
        best_idx = int(np.argmax(sims))
        best = all_chunks[best_idx]
        print(f"\nQuery: {query}")
        print(f"  Top match ({sims[best_idx]:.3f}) from {best['source']} [chunk {best['chunk_id']}]:")
        preview = best["text"][:160].replace("\n", " ")
        print(f"  \"{preview}...\"")

    # Persist embeddings + chunk metadata for reuse when the vector DB is built in Checkpoint 2.
    np.save(OUT_DIR / "sample_chunk_embeddings.npy", chunk_embeddings)
    with open(OUT_DIR / "sample_chunks.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2)
    print(f"\nSaved {len(all_chunks)} chunk embeddings to {OUT_DIR}")


if __name__ == "__main__":
    main()
