# Presenting Checkpoints 1 & 2 — Step-by-Step Guide

A run-of-show for demoing Checkpoint 1 (Foundation & Data Pipeline) and
Checkpoint 2 (Prompt Architecture & Vector Indexing) live — exact commands,
what each one proves, and what to say while it runs. Budget ~12-15 minutes
total (5-6 min CP1, 6-8 min CP2, rest buffer for questions).

---

## 0. Before you present (do this once, beforehand — not live)

```bash
python3 -m venv .venv
.venv\Scripts\activate          # Windows;  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

- Copy `.env.example` to `.env` and paste your Gemini key in (get a free one
  at [aistudio.google.com/apikey](https://aistudio.google.com/apikey) if you
  don't have one). **Never show this file on screen** — it holds your API key.
- Run the whole pipeline once end-to-end so nothing fails live from a cold
  cache (model weight downloads, etc. — see the exact commands in Parts A
  and B below).
- Have these files open in tabs, ready to flash on screen:
  - `docs/Project_Proposal.docx`
  - `docs/Data_Sources.md`
  - `docs/Reflection_Checkpoint1.md`
  - `docs/Prompt_Engineering.md`
  - `docs/Distance_Metric_Comparison.md`
  - `README.md`

---

## Part A — Checkpoint 1: Foundation & Data Pipeline

**One-line framing to open with:** *"Pathfinder is a RAG academic advisor
for TPC's BSIS program. Checkpoint 1 proves we can turn messy real-world
text — and a real gap where the data doesn't exist — into something a model
can reason over."*

### A1. Show the proposal (30 sec)

Open `docs/Project_Proposal.docx`. Point to: problem statement, target
users (BSIS students), chosen theme, dataset sources, success criteria.

### A2. Show data provenance — the honesty angle (1 min)

Open `docs/Data_Sources.md`. Say: *"30 documents total — 16 are real,
scraped from TPC's public website. The other 14 don't exist on TPC's site
at all — the curriculum checklist and academic policies live in a 52-page
student handbook that's preview-locked on Scribd. Instead of quietly
inventing course requirements, we built that half of the dataset from CHED
Memorandum Order 25, s. 2015 — the actual national policy that governs BSIS
programs in the Philippines — and every simulated file is labeled
`[SIMULATED DATA]` in its first line."* This is your strongest "Problem &
Scope Clarity" talking point — lead with it, don't bury it.

### A3. Run the pipeline, in order

```bash
python3 src/00_generate_curriculum_data.py
```
Say: *"This generates the CHED-based simulated curriculum and policy
documents — 12 curriculum files, 2 policy files."*

```bash
python3 src/01_extract_raw_text.py
```
Say: *"This extracts plain text from the 16 raw HTML pages we scraped from
tpc.edu.ph, using BeautifulSoup — not a regex tag-stripper, which we
initially tried and it leaked raw JavaScript into the text (see the
reflection doc for exactly what went wrong)."*

```bash
python3 src/02_preprocess.py
```
Watch for: printed before/after examples in the terminal. Say: *"This
strips ~35 lines of repeated site-chrome per page — nav links, footer,
a feedback widget — and fixes a Cloudflare email-obfuscation artifact. Cut
total corpus size by about 28% without losing any advising content."*

```bash
python3 src/03_generate_embeddings.py
```
Watch for: the retrieval sanity-check output at the end (semantically
similar queries landing close together in embedding space). Say: *"We use
`all-MiniLM-L6-v2` — open-source, runs fully local, no API cost, 384-dim
embeddings sized right for a corpus this size."*

### A4. Close with the reflection (30 sec)

Open `docs/Reflection_Checkpoint1.md`. Read the last paragraph aloud — the
embedding demo surfaced a real retrieval quality issue (whole-document
chunking causing a table to outrank a more specific paragraph) that
foreshadows Checkpoint 2/3 work. This shows the reflection wasn't
retrofitted — it's a real finding.

**CP1 rubric cheat sheet:**

| Rubric line | Where the evidence is |
|---|---|
| Problem & Scope Clarity | `Project_Proposal.docx` + the "16 real / 14 simulated" framing |
| Data Preprocessing | `02_preprocess.py` terminal output (before/after) |
| Embedding Generation | `03_generate_embeddings.py` + its docstring's model justification |
| Documentation & Repo Hygiene | `README.md`, commit history, `Data_Sources.md` |

---

## Part B — Checkpoint 2: Prompt Architecture & Vector Indexing

**One-line framing to open with:** *"Checkpoint 2 proves two things: we can
constrain the model's behavior with structured prompts, and we can stand up
a real, queryable vector index over the full corpus."*

### B1. Build the vector index (1 min)

```bash
python3 src/04_setup_vector_db.py
```
Watch for: `Indexed 109 chunks from 30 documents...` then 5 similarity-search
results. Say: *"This chunks and embeds all 30 documents — not just the
5-doc sample from Checkpoint 1 — into a persistent Chroma collection using
cosine similarity. Point at one result on screen, e.g. the academic
probation query correctly pulling the exact policy chunk with the 15-unit
cap."*

### B2. Distance metric comparison (1-2 min)

```bash
python3 src/05_distance_metric_comparison.py
```
Open `docs/Distance_Metric_Comparison.md` alongside. Say: *"We compared
cosine, Euclidean, and dot product by hand on our own embeddings — and got
an interesting result: all three produced identical rankings, because
`all-MiniLM-L6-v2` has a built-in normalization layer, so cosine and dot
product become mathematically identical and Euclidean becomes a monotonic
transform of cosine. That's a real finding, not a hedge — the doc explains
the math and still gives a defensible recommendation."* This is a great
"why this and not that" answer if asked in Q&A.

### B3. Prompt engineering + live API demo (3-4 min — the centerpiece)

Open `docs/Prompt_Engineering.md` briefly first. Say: *"We designed 4
structured system prompts, each targeting a specific failure mode:
hallucinating facts, inventing a fake prerequisite chain, answering
off-topic questions, and confidently answering an ambiguous question. Every
example in this doc is a real captured model transcript, not something we
wrote by hand."*

Then run it live:

```bash
python3 src/06_api_integration_demo.py
```

This runs 4 fixed test cases automatically (narrate briefly as they scroll:
grounded answer with citation → refuses to invent IS999's prerequisites →
declines the poem/trivia request → asks for the missing year/semester
instead of guessing), then drops into **live query mode**:

```
Your question: <type here>
```

**Type 2-3 of these live**, picking a mix so the room sees different
behaviors, not just correct answers:

| Question to type | What it demonstrates |
|---|---|
| `What are the prerequisites for IS205 Information Management 1?` | A clean grounded answer with citation |
| `How many units can I enroll in while on academic probation?` | Correct retrieval of an exact policy figure (15 units) |
| `What GWA do I need to graduate Cum Laude?` | Correct retrieval of a specific number (1.75) |
| `What's the weather like today?` | Off-topic refusal, live, unscripted |
| `What subjects should I take next?` | Ambiguity handling — the assistant asks which year/semester instead of guessing |
| `What are the prerequisites for IS777 Blockchain for Farmers?` | Live hallucination-trap — a course we made up on the spot |

Type `quit` to exit the loop when done.

**If you get a live API error (rate limit, network hiccup):** don't panic —
say *"this is actually a good demonstration of the error handling we built
in — instead of crashing, it reports the failure and we can retry."* Then
either retry once, or fall back to reading the pre-captured transcripts in
`docs/_api_demo_transcripts.md` / `docs/Prompt_Engineering.md`.

**CP2 rubric cheat sheet:**

| Rubric line | Where the evidence is |
|---|---|
| Prompt Design Quality | `docs/Prompt_Engineering.md` — 4 prompts, each with real transcript |
| API Integration | `06_api_integration_demo.py` live run + its error handling |
| Vector Database Implementation | `04_setup_vector_db.py` — 109 chunks, cosine, sensible results |
| Distance Metric Analysis | `docs/Distance_Metric_Comparison.md` |

---

## Fallback / troubleshooting during the live demo

- **Chroma index missing or stale:** re-run `python3 src/04_setup_vector_db.py`
  before `06_api_integration_demo.py` — it rebuilds cleanly every time.
- **`GEMINI_API_KEY not set` error:** you forgot to fill in `.env` on this
  machine — check it's not still `your-gemini-api-key-here`.
- **429 / quota error:** the demo already standardizes on
  `gemini-3.5-flash-lite` specifically because the flagship model's free
  tier caps at 20 requests/day (we hit this during development — see the
  note at the top of `docs/Prompt_Engineering.md`). If it still happens,
  that's your daily quota on this key — fall back to the saved transcripts.
- **A live query gets an unexpectedly weak answer:** that's fine to narrate
  honestly — e.g. *"this shows a real limitation: whole-document-adjacent
  chunking sometimes splits a table row, which is exactly the chunking
  issue flagged in our Checkpoint 1 reflection and something we're
  addressing in Checkpoint 3's ingestion pipeline."* Owning a real
  limitation reads better than pretending there isn't one.
