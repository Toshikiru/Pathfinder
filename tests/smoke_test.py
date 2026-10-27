"""
Offline smoke tests - no GEMINI_API_KEY and no network needed, so they can run
in CI and inside the built Docker image:

    docker run --rm pathfinder python tests/smoke_test.py

They exercise everything up to (but not including) the LLM call: term
detection, the shipped Chroma index, and real retrieval against it. The
expected sources are the ones recorded in docs/_rag_app_demo_transcripts.md.
"""

import importlib.util
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rag = load("pathfinder_rag_app", "src/08_rag_app.py")
_store = None


def store():
    global _store
    if _store is None:
        _store = rag.get_vectorstore()
    return _store


def test_detect_term():
    assert rag.detect_term("How many subjects are in first year first sem?") == (1, 1)
    assert rag.detect_term("what about second year second semester") == (2, 2)
    assert rag.detect_term("What is the GWA for Latin honors?") == (None, None)


def test_extract_text_handles_both_gemini_shapes():
    assert rag.extract_text("plain") == "plain"
    assert rag.extract_text([{"type": "text", "text": "a"}, {"type": "text", "text": "b"}]) == "ab"


def test_live_advisor_prompt_present():
    assert "TPC" in rag.PROMPTS["live_advisor"]


def test_index_is_populated():
    count = store()._collection.count()
    assert count >= 50, f"index looks empty/truncated: {count} chunks"


def test_policy_query_retrieves_grading_policy():
    docs = store().similarity_search("What is the GWA requirement for Latin honors?", k=4)
    sources = [d.metadata["source"] for d in docs]
    assert any("grading_system_and_gwa_policy" in s for s in sources), sources


def test_term_filter_returns_only_requested_term():
    docs = store().similarity_search(
        "courses in first year first semester",
        k=3,
        filter={"$and": [{"year": 1}, {"semester": 1}]},
    )
    assert docs, "filter returned nothing"
    assert {d.metadata["source"] for d in docs} == {"curriculum/01_year_1_first_semester.txt"}


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception:
            failed += 1
            print(f"FAIL  {name}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
