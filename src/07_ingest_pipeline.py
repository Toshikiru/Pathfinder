"""
Checkpoint 3, Deliverable 10 - Ingestion Pipeline
Orchestrates the existing per-stage scripts (01, 02, 04) into one automated,
end-to-end command: raw HTML/text in data/raw/ -> extracted -> cleaned ->
chunked -> embedded -> stored in the Chroma index. Drop a new document into
data/raw/ (a new .html page under tpc_website_html/, or a new .txt under
curriculum/ or policies/) and run this one script to re-ingest the full
corpus - no manual multi-script sequence required.

This is intentionally a thin orchestrator, not new pipeline logic: each stage
already exists and is independently tested (Checkpoints 1-2). Reuses the same
importlib pattern 06_api_integration_demo.py already uses to import a
numbered module.
"""

import importlib.util
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGE_FILES = {
    "extract": ROOT / "01_extract_raw_text.py",
    "preprocess": ROOT / "02_preprocess.py",
    "index": ROOT / "04_setup_vector_db.py",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    print("=" * 90)
    print("INGESTION PIPELINE - raw documents -> extracted -> cleaned -> chunked -> embedded -> indexed")
    print("=" * 90)
    t0 = time.time()

    print("\n[1/3] Extracting raw text from saved HTML (data/raw/tpc_website_html/ -> data/raw/tpc_website/)")
    extract = load_module("extract_raw_text", STAGE_FILES["extract"])
    extract.main()

    print("\n[2/3] Cleaning + normalizing all raw documents (data/raw/ -> data/processed/)")
    preprocess = load_module("preprocess", STAGE_FILES["preprocess"])
    manifest = preprocess.process_all()
    print(f"Processed {len(manifest)} documents.")

    print("\n[3/3] Chunking, embedding, and (re)building the Chroma vector index")
    setup_vector_db = load_module("setup_vector_db", STAGE_FILES["index"])
    setup_vector_db.build_index()

    elapsed = time.time() - t0
    print(f"\nIngestion complete in {elapsed:.1f}s. The corpus in data/raw/ is now fully "
          f"reflected in the 'pathfinder_bsis_advisor' Chroma collection.")


if __name__ == "__main__":
    main()
