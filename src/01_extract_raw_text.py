"""
Stage 1 - Data Collection
Extracts visible page text from the saved Talibon Polytechnic College (TPC)
website HTML pages (data/raw/tpc_website_html/) into plain-text documents
(data/raw/tpc_website/). This is intentionally the RAW layer: text is pulled
straight from each page's DOM in reading order and NOT cleaned yet (repeated
nav/footer text, inconsistent whitespace, and stray UI copy like "Close" or
"Feedback" are left in on purpose). Cleaning happens in 02_preprocess.py.

Source: https://www.tpc.edu.ph/ (public pages, fetched 2026-08-24).
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
HTML_DIR = ROOT / "data" / "raw" / "tpc_website_html"
OUT_DIR = ROOT / "data" / "raw" / "tpc_website"


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")

    # Drop elements that never carry advising-relevant content.
    for tag in soup(["script", "style", "svg", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Collapse runs of blank/whitespace-only lines but keep raw messiness
    # (duplicate nav links, inconsistent spacing) for the preprocessing demo.
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html_files = sorted(HTML_DIR.glob("*.html"))
    if not html_files:
        raise SystemExit(f"No HTML files found in {HTML_DIR}")

    for html_path in html_files:
        html = html_path.read_text(encoding="utf-8")
        text = extract_text(html)
        out_path = OUT_DIR / (html_path.stem + ".txt")
        out_path.write_text(text, encoding="utf-8")
        print(f"{html_path.name:70s} -> {out_path.name:50s} ({len(text.split())} words)")


if __name__ == "__main__":
    main()
