"""
Measures the proposal's Performance success criterion:
"retrieval latency (query embedding + similarity search) stays under 2 seconds
on the full corpus." Needs no API key (retrieval only; no LLM call).

    python tests/measure_retrieval_latency.py
    docker run --rm pathfinder python tests/measure_retrieval_latency.py
"""

import importlib.util
import statistics
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("pathfinder_rag_app", ROOT / "src" / "08_rag_app.py")
rag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag)

QUERIES = [
    "What are the prerequisites for IS 104 System Analysis & Design?",
    "What's the GWA requirement for Latin honors?",
    "How many units can I enroll in if I'm on academic probation?",
    "What do I need before enrolling in Capstone Project I?",
    "Who handles enrollment at the registrar's office?",
    "What are the admission requirements for incoming first-year students?",
    "What are the prerequisites for CC 105?",
    "How is GWA computed?",
]
RUNS_PER_QUERY = 5

store = rag.get_vectorstore()
store.similarity_search("warm-up", k=rag.K)  # exclude one-time model/index warm-up from timings

timings = []
for q in QUERIES:
    for _ in range(RUNS_PER_QUERY):
        t0 = time.perf_counter()
        store.similarity_search(q, k=rag.K)
        timings.append(time.perf_counter() - t0)

timings.sort()
p95 = timings[int(0.95 * (len(timings) - 1))]
print(f"{len(timings)} retrievals over {len(QUERIES)} queries (k={rag.K}, warm)")
print(f"mean {statistics.mean(timings)*1000:.0f} ms | median {statistics.median(timings)*1000:.0f} ms | "
      f"p95 {p95*1000:.0f} ms | max {timings[-1]*1000:.0f} ms")
print("PASS (< 2 s)" if timings[-1] < 2.0 else "FAIL (>= 2 s on at least one retrieval)")
