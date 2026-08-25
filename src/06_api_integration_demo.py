"""
Checkpoint 2, Deliverable 7 - API Integration Demo
Sends the prompts from prompts.py to the Gemini Chat Completion API, grounded
in context retrieved from the Chroma vector index (04_setup_vector_db.py).
Each test case is chosen to exercise a specific prompt's safeguard:

  1. grounded_advisor  - answers a real, in-scope question correctly.
  2. prerequisite_verifier - asked about a course code that does NOT exist in
     the corpus, to check the model refuses to invent a prerequisite chain.
  3. scope_guard - asked something entirely unrelated to academic advising.
  4. clarification - asked an ambiguous question with no year/semester given.

Requires GEMINI_API_KEY in .env (see .env.example). Free key:
https://aistudio.google.com/apikey

Transcripts are saved to docs/_api_demo_transcripts.md and quoted directly
in docs/Prompt_Engineering.md - these are real model outputs, not
hand-written examples.

After the 4 fixed cases run, drops into a live query loop so you can type
your own questions and get real grounded answers on the spot (uses the
combined `live_advisor` prompt, which merges the grounding/scope/ambiguity
rules from the 4 individual prompts above into one - see prompts.py).
Type 'quit', 'exit', or an empty line to stop.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from prompts import PROMPTS  # noqa: E402
import importlib.util

spec = importlib.util.spec_from_file_location("setup_vector_db", ROOT / "src" / "04_setup_vector_db.py")
setup_vector_db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup_vector_db)

MODEL_NAME = "gemini-3.5-flash-lite"
# NOTE: the flagship "gemini-3.6-flash" free tier caps at 20 requests/DAY,
# which is unworkable for iterative dev/demo/grading re-runs. The "-lite"
# line has a much higher free-tier daily quota with only a modest quality
# tradeoff, and is what this project standardizes on for CP2+.
TRANSCRIPT_PATH = ROOT / "docs" / "_api_demo_transcripts.md"

TEST_CASES = [
    {
        "label": "1. Grounded answer (grounded_advisor prompt)",
        "prompt_key": "grounded_advisor",
        "question": "What are the prerequisites for IS301 Systems Analysis and Design, and how many units is it?",
        "purpose": "Confirms the assistant answers correctly and cites the source when the answer IS in the knowledge base.",
    },
    {
        "label": "2. Hallucination trap (prerequisite_verifier prompt)",
        "prompt_key": "prerequisite_verifier",
        "question": "What are the prerequisites for IS999 Advanced Quantum Computing for Business?",
        "purpose": "IS999 does not exist anywhere in the corpus. Confirms the assistant reports 'not found' instead of inventing a plausible-sounding prerequisite chain.",
    },
    {
        "label": "3. Off-topic refusal (scope_guard prompt)",
        "prompt_key": "scope_guard",
        "question": "Can you write me a 4-line poem about cats, and also what's the capital of France?",
        "purpose": "Entirely unrelated to TPC/BSIS advising. Confirms the assistant declines and redirects instead of answering the trivia/creative-writing request.",
    },
    {
        "label": "4. Ambiguous query (clarification prompt)",
        "prompt_key": "clarification",
        "question": "What subjects should I take next semester?",
        "purpose": "No year/semester or completed-courses info given, and the corpus has 9 different terms. Confirms the assistant asks for the missing info instead of guessing a term.",
    },
]


def build_contents(system_prompt: str, context: str, question: str) -> str:
    return (
        f"{system_prompt}\n\n"
        f"CONTEXT:\n{context}\n\n"
        f"QUESTION: {question}"
    )


def run_case(client: genai.Client, case: dict) -> dict:
    try:
        hits = setup_vector_db.query(case["question"], k=4)
    except Exception as exc:
        return {**case, "retrieved_sources": [], "answer": f"[RETRIEVAL ERROR] {exc}"}

    if not hits:
        return {**case, "retrieved_sources": [], "answer": "[NO CONTEXT RETRIEVED - index may be empty. Run 04_setup_vector_db.py first.]"}

    context = "\n\n---\n\n".join(f"[{h['source']}]\n{h['text']}" for h in hits)
    system_prompt = PROMPTS[case["prompt_key"]]
    contents = build_contents(system_prompt, context, case["question"])

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=contents)
    except Exception as exc:
        # Covers rate limits, invalid/expired key, network errors, etc.
        return {**case, "retrieved_sources": [h["source"] for h in hits],
                "answer": f"[API ERROR] {type(exc).__name__}: {exc}"}

    answer_text = getattr(response, "text", None)
    if not answer_text:
        # Empty response can happen if the safety filter blocks output.
        finish_reason = getattr(getattr(response, "candidates", [None])[0], "finish_reason", "unknown")
        answer_text = f"[EMPTY RESPONSE - finish_reason={finish_reason}]"

    return {
        "label": case.get("label", "Live query"),
        "purpose": case.get("purpose", ""),
        "prompt_key": case["prompt_key"],
        "question": case["question"],
        "retrieved_sources": [h["source"] for h in hits],
        "answer": answer_text,
    }


def main():
    load_dotenv(ROOT / ".env")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        raise SystemExit(
            "GEMINI_API_KEY not set. Copy .env.example to .env and paste your "
            "free key from https://aistudio.google.com/apikey"
        )

    client = genai.Client(api_key=api_key)

    results = []
    lines = ["# API Integration Demo - Real Model Transcripts\n",
             f"Model: `{MODEL_NAME}` via the Gemini API. Each case retrieves context "
             f"from the Chroma index built in `04_setup_vector_db.py`, then applies one "
             f"of the four system prompts from `prompts.py`.\n"]

    for case in TEST_CASES:
        print(f"\n{'=' * 90}\n{case['label']}\n{'=' * 90}")
        print(f"Purpose: {case['purpose']}")
        print(f"Question: {case['question']}")
        result = run_case(client, case)
        results.append(result)
        print(f"Retrieved: {result['retrieved_sources']}")
        print(f"\nAnswer:\n{result['answer']}")

        lines.append(f"\n## {result['label']}\n")
        lines.append(f"**Purpose:** {result['purpose']}\n")
        lines.append(f"**System prompt used:** `{result['prompt_key']}`\n")
        lines.append(f"**Question:** {result['question']}\n")
        lines.append(f"**Retrieved context sources:** {', '.join(result['retrieved_sources'])}\n")
        lines.append(f"**Model answer:**\n\n> {result['answer'].replace(chr(10), chr(10) + '> ')}\n")

    TRANSCRIPT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n\nSaved full transcripts to {TRANSCRIPT_PATH}")

    live_query_loop(client)


def live_query_loop(client: genai.Client) -> None:
    print(f"\n{'=' * 90}\nLIVE QUERY MODE - ask Pathfinder anything about TPC's BSIS program\n{'=' * 90}")
    print("(type 'quit', 'exit', or an empty line to stop)\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting live query mode.")
            break

        if not question or question.lower() in {"quit", "exit"}:
            print("Exiting live query mode.")
            break

        case = {"question": question, "prompt_key": "live_advisor"}
        result = run_case(client, case)
        print(f"Retrieved: {result['retrieved_sources']}")
        print(f"\nAnswer:\n{result['answer']}\n")


if __name__ == "__main__":
    main()
