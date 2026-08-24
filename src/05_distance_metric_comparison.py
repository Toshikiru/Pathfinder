"""
Checkpoint 2, Deliverable 9 - Distance Metric Comparison
Computes Cosine similarity, Euclidean (L2) distance, and Dot Product on the
SAME chunk embeddings from our own corpus, for the same set of realistic
advising queries, and prints the top-3 result per metric side by side so the
differences (if any) are visible on real data rather than argued abstractly.

Embeddings are NOT pre-normalized here (unlike 03_generate_embeddings.py)
specifically so dot product and cosine can actually diverge - if every
vector already has unit norm, dot product and cosine are mathematically
identical and the comparison would be meaningless.
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"
OUT_PATH = ROOT / "docs" / "_distance_metric_results.json"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

QUERIES = [
    "What are the prerequisites for Systems Analysis and Design?",
    "How many units can I enroll in while on academic probation?",
    "Who is the program head of BSIS?",
    "What GWA do I need for Latin honors?",
]


def chunk_text(text: str, max_chars: int = 500) -> list[str]:
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


def cosine_sim(query_vec, matrix):
    q = query_vec / np.linalg.norm(query_vec)
    m = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return m @ q  # higher = more similar


def euclidean_dist(query_vec, matrix):
    return np.linalg.norm(matrix - query_vec, axis=1)  # lower = more similar


def dot_product(query_vec, matrix):
    return matrix @ query_vec  # higher = more similar (NOT normalized)


def main():
    model = SentenceTransformer(MODEL_NAME)

    chunks = []
    for path in sorted(PROCESSED_DIR.rglob("*.txt")):
        if path.name == "_manifest.json":
            continue
        rel = str(path.relative_to(PROCESSED_DIR)).replace("\\", "/")
        text = path.read_text(encoding="utf-8")
        for i, c in enumerate(chunk_text(text)):
            chunks.append({"source": rel, "chunk_id": i, "text": c})

    texts = [c["text"] for c in chunks]
    # Deliberately UNNORMALIZED embeddings for this comparison.
    matrix = model.encode(texts, normalize_embeddings=False, show_progress_bar=False)
    norms = np.linalg.norm(matrix, axis=1)
    print(f"Embedded {len(chunks)} chunks. Norm range: {norms.min():.3f} - {norms.max():.3f} "
          f"(non-uniform, so dot product and cosine CAN disagree)\n")

    all_results = {}
    for query in QUERIES:
        qvec = model.encode([query], normalize_embeddings=False)[0]

        cos = cosine_sim(qvec, matrix)
        euc = euclidean_dist(qvec, matrix)
        dot = dot_product(qvec, matrix)

        top_cos = np.argsort(-cos)[:3]
        top_euc = np.argsort(euc)[:3]
        top_dot = np.argsort(-dot)[:3]

        print("=" * 95)
        print(f"Query: {query}")
        print("-" * 95)
        for name, idxs, scores, higher_is_better in [
            ("COSINE", top_cos, cos, True),
            ("EUCLIDEAN", top_euc, euc, False),
            ("DOT PRODUCT", top_dot, dot, True),
        ]:
            print(f"\n  {name} (top 3, {'higher' if higher_is_better else 'lower'} = more similar):")
            for rank, idx in enumerate(idxs, 1):
                c = chunks[idx]
                preview = c["text"][:100].replace("\n", " ")
                print(f"    {rank}. score={scores[idx]:.4f}  {c['source']}#{c['chunk_id']}")
                print(f"       \"{preview}...\"")

        all_results[query] = {
            "cosine_top": [chunks[i]["source"] for i in top_cos],
            "euclidean_top": [chunks[i]["source"] for i in top_euc],
            "dot_product_top": [chunks[i]["source"] for i in top_dot],
            "agreement_cosine_vs_euclidean": bool(set(top_cos.tolist()) == set(top_euc.tolist())),
            "agreement_cosine_vs_dot": bool(set(top_cos.tolist()) == set(top_dot.tolist())),
        }

    OUT_PATH.write_text(json.dumps(all_results, indent=2), encoding="utf-8")
    print(f"\nSaved machine-readable results to {OUT_PATH}")


if __name__ == "__main__":
    main()
