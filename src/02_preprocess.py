"""
Stage 2 - Text Preprocessing
Cleans and normalizes every document in data/raw/ (the TPC website scrape,
the simulated curriculum checklists, and the simulated policy docs) and
writes the result to data/processed/. Also prints a handful of concrete
before/after examples so the cleaning is demonstrably working, and writes
tokenization stats used in the Checkpoint 1 reflection.

Cleaning steps applied (in order):
  1. Strip site-wide navigation/UI boilerplate that repeats on every TPC
     page (nav links, search widget copy, footer, cookie/feedback widget).
     This is the single biggest source of noise in the raw scrape.
  2. Fix the Cloudflare email-obfuscation placeholder ("[email protected]")
     left behind by the scraper.
  3. Collapse duplicate/blank lines and normalize whitespace.
  4. Lowercase + strip punctuation for a *tokenization* pass (kept as a
     separate field, not applied to the human-readable cleaned text, since
     a RAG retriever wants natural casing/punctuation for the LLM to read
     but a word-level view is useful for the embedding/tokenization demo).
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# Lines that are pure site-chrome boilerplate on every scraped TPC page.
# Collected by inspecting the raw extraction output for repeated lines.
BOILERPLATE_LINES = {
    "talibon polytechnic college",
    "official website",
    "home", "about", "academics", "services", "our services",
    "guidance and counseling center", "registrar's office", "registrar’s office",
    "admission", "news", "contact",
    "results", "↑↓ navigate", "·", "enter to go", "esc to close",
    'no results for "', '"', "try a page name or section", "navigation",
    "back to programs", "how to enroll", "ask a question",
    "organizational chart", "see the full administration and academic leadership structure of talibon polytechnic college.",
    "committed to providing accessible, high-quality education through academic",
    "excellence, innovation, and service to the community.",
    "facebook page", "© 2026 talibon polytechnic college. all rights reserved.",
    "|", "/", "secrit solutions: aabjrsv", "feedback", "tpc feedback",
    "your feedback helps us improve. we appreciate you taking the time.",
    "close", "how would you rate your experience?", "*", "category",
    "general", "facilities", "faculty & instruction", "website / online services",
    "other", "comments", "add contact info (optional)", "your name", "your email",
    "leave these blank to stay anonymous. we'll only use them if you'd like a reply.",
    "anonymous by default", "interested?", "view admission guide", "contact us",
    "other programs", "explore programs before enrolling",
    "view all academic programs offered by talibon polytechnic college.",
    "view programs", "updates →",
}

EMAIL_PLACEHOLDER = re.compile(r"\[email[\s_-]?protected\]", re.IGNORECASE)
WHITESPACE_RUN = re.compile(r"[ \t]+")


def clean_text(raw: str) -> str:
    lines = raw.split("\n")
    cleaned_lines = []
    prev = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower() in BOILERPLATE_LINES:
            continue
        stripped = EMAIL_PLACEHOLDER.sub("registrar@tpc.edu.ph", stripped)
        stripped = WHITESPACE_RUN.sub(" ", stripped)
        if stripped == prev:  # drop immediate duplicates (nav repeated twice)
            continue
        cleaned_lines.append(stripped)
        prev = stripped
    return "\n".join(cleaned_lines)


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z]+)?")


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def process_all() -> list[dict]:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    src_files = sorted(RAW_DIR.rglob("*.txt"))
    for src in src_files:
        raw = src.read_text(encoding="utf-8")
        cleaned = clean_text(raw)
        tokens = tokenize(cleaned)

        rel = src.relative_to(RAW_DIR)
        out_path = PROCESSED_DIR / rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(cleaned, encoding="utf-8")

        manifest.append({
            "source": str(rel).replace("\\", "/"),
            "raw_chars": len(raw),
            "raw_lines": len(raw.splitlines()),
            "cleaned_chars": len(cleaned),
            "cleaned_lines": len(cleaned.splitlines()),
            "token_count": len(tokens),
            "unique_tokens": len(set(tokens)),
        })
    (PROCESSED_DIR / "_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest


def print_before_after_examples() -> None:
    examples = [
        RAW_DIR / "tpc_website" / "academics_bachelor-of-science-in-information-systems.txt",
        RAW_DIR / "curriculum" / "05_year_3_first_semester.txt",
    ]
    for src in examples:
        if not src.exists():
            continue
        raw = src.read_text(encoding="utf-8")
        cleaned = clean_text(raw)
        print("=" * 90)
        print(f"BEFORE / AFTER: {src.relative_to(RAW_DIR)}")
        print("-" * 90)
        print("RAW (first 8 lines):")
        for line in raw.splitlines()[:8]:
            print(f"  | {line}")
        print("-" * 90)
        print("CLEANED (first 8 lines):")
        for line in cleaned.splitlines()[:8]:
            print(f"  | {line}")
        print(f"\nraw: {len(raw.splitlines())} lines / {len(raw)} chars  ->  "
              f"cleaned: {len(cleaned.splitlines())} lines / {len(cleaned)} chars")


if __name__ == "__main__":
    print_before_after_examples()
    print("\n" + "=" * 90)
    manifest = process_all()
    total_raw_chars = sum(m["raw_chars"] for m in manifest)
    total_clean_chars = sum(m["cleaned_chars"] for m in manifest)
    total_tokens = sum(m["token_count"] for m in manifest)
    print(f"Processed {len(manifest)} documents.")
    print(f"Total raw chars: {total_raw_chars:,} -> cleaned chars: {total_clean_chars:,} "
          f"({100 * (1 - total_clean_chars / total_raw_chars):.1f}% noise removed)")
    print(f"Total tokens across corpus: {total_tokens:,}")
