# Pathfinder: A RAG-based Academic Advisor

Mini Generative AI Capstone Project — IS Professional Elective #4 (Generative AI Systems)
Talibon Polytechnic College · 1st Semester, A.Y. 2026–2027 · Instructor: Jessie A. Melendres

**Theme:** Document/Knowledge-Base Q&A Assistant, specialized for academic advising —
a RAG chatbot grounded in TPC's BSIS curriculum, course prerequisites, and academic
policies, so students can ask course-planning and degree-progress questions and get
a cited, non-hallucinated answer instead of manually cross-referencing a checklist.

**Scope:** "Academic advising" here covers everything a currently-enrolled BSIS student
needs to plan a term and track graduation — course planning (prerequisites, curriculum
checklist) and degree progress (grading scale, GWA computation, Latin honors, academic
standing). The grading/GWA policy is in-scope for exactly this reason: computing and
interpreting GWA is a degree-progress question, not a separate topic.

## Checkpoint status

- [x] **Checkpoint 1 — Foundation & Data Pipeline** (Prelim): proposal, dataset,
      preprocessing, embedding demo. *Complete.*
- [x] **Checkpoint 2 — Prompt Architecture & Vector Indexing** (Midterm): prompt
      engineering doc, Gemini API integration, Chroma vector DB, distance metric
      comparison. *Complete — see below.*
- [x] **Checkpoint 3 — RAG Orchestration & Working Application** (Semi-Final):
      automated ingestion pipeline, LangChain-orchestrated RAG app with
      multi-turn memory, LlamaIndex comparison demo, framework comparison
      note. *Complete — see below.*
- [ ] Checkpoint 4 — Customization, Deployment & Final Defense (Final)

## Repository layout

```
data/
  raw/
    tpc_website_html/   10 raw HTML pages scraped from tpc.edu.ph (source of truth)
    tpc_website/        same 10 pages, extracted to plain text (still messy - real "raw" layer)
    curriculum/         8 REAL official BSIS curriculum-checklist files + 3 simulated course-description docs
    policies/           2 simulated academic-policy docs
  processed/             output of 02_preprocess.py (cleaned text + _manifest.json)
    _embeddings/          output of 03_generate_embeddings.py (sample chunk vectors)
src/
  00_generate_curriculum_data.py   writes the real curriculum checklist + simulated descriptions/policy documents
  01_extract_raw_text.py           HTML -> raw text (BeautifulSoup)
  02_preprocess.py                 raw text -> cleaned text, prints before/after examples
  03_generate_embeddings.py        embedding generation + retrieval sanity check (CP1 sample)
  04_setup_vector_db.py            chunks + embeds the FULL corpus into a persistent Chroma index
  05_distance_metric_comparison.py cosine vs euclidean vs dot product on our own data
  06_api_integration_demo.py       retrieval + system prompts -> real Gemini API calls
  07_ingest_pipeline.py            CP3: orchestrates 01 -> 02 -> 04 into one automated ingestion command
  08_rag_app.py                    CP3: LangChain RAG app with multi-turn conversational memory
  09_llamaindex_comparison.py      CP3: LlamaIndex comparison-only demo (not used in production)
  prompts.py                       the 5 structured system/instruction prompts
scripts/
  fill_proposal.py        fills docs/Project_Proposal.docx from the instructor's template
docs/
  Project_Proposal.docx   Checkpoint 1 deliverable
  Data_Sources.md          full provenance of every document in data/raw
  Reflection_Checkpoint1.md
  Prompt_Engineering.md            Checkpoint 2 deliverable (quotes real Gemini transcripts)
  Distance_Metric_Comparison.md    Checkpoint 2 deliverable
  Framework_Comparison_Note.md     Checkpoint 3 deliverable (LangChain vs LlamaIndex, with real output)
  _api_demo_transcripts.md         raw transcripts referenced by Prompt_Engineering.md
  _distance_metric_results.json    raw results referenced by Distance_Metric_Comparison.md
  _rag_app_demo_transcripts.md     raw multi-turn transcripts from 08_rag_app.py
  Presentation_Guide_CP1_CP2.md    step-by-step run-of-show for demoing CP1+CP2 live
```

## Data sources (summary — full detail in [docs/Data_Sources.md](docs/Data_Sources.md))

23 documents total:
- **10 real**, scraped from TPC's public website (`tpc.edu.ph`): BSIS program
  description, admission requirements, enrollment process, registrar/guidance
  services, contact info. (6 pages about *other* TPC degree programs were
  scraped originally but removed as out-of-scope once the corpus had other
  real content to meet the document minimum — see Data_Sources.md.)
- **8 real**, transcribed from a printed, signed copy of TPC's official BSIS
  curriculum checklist (effective A.Y. 2024–2025, based on CHED Memorandum
  Order No. 25 s. 2015 and CMO No. 20 s. 2013): 8 terms (Year 1–4, no summer
  term), with real course codes, titles, units, lecture/lab hours, and
  prerequisites. TPC doesn't publish this online, but a physical copy was
  obtained directly — every file is labeled `[REAL DATA]` in its first line.
- **5 simulated**: a course-description catalog (3 files, real course codes
  from the checklist above, authored descriptions) and academic policy
  documents (2 files: grading/GWA, enrollment/academic-standing) — TPC's full
  student handbook isn't accessible, so this gap is filled transparently;
  every simulated file is labeled `[SIMULATED DATA]` in its first line.

## Setup

```bash
python3 -m venv .venv
.venv\Scripts\activate #on Windows
pip install -r requirements.txt
cp .env.example .env        # then paste your free Gemini key (aistudio.google.com/apikey)
```

## Running the Checkpoint 1 pipeline

```bash
python3 src/00_generate_curriculum_data.py   # writes data/raw/curriculum/, data/raw/policies/
python3 src/01_extract_raw_text.py           # writes data/raw/tpc_website/ from saved HTML
python3 src/02_preprocess.py                 # writes data/processed/, prints before/after
python3 src/03_generate_embeddings.py        # embeds a sample + prints retrieval sanity check
```

`sentence-transformers/all-MiniLM-L6-v2` (open-source, local, 384-dim) is used
for embeddings — no API key required. See the module docstring in
`03_generate_embeddings.py` for the model choice rationale.

## Running the Checkpoint 2 pipeline

```bash
python3 src/04_setup_vector_db.py            # builds the full 105-chunk Chroma index, runs a similarity-search demo
python3 src/05_distance_metric_comparison.py # cosine/euclidean/dot-product comparison -> docs/_distance_metric_results.json
python3 src/06_api_integration_demo.py       # retrieval + prompts -> real Gemini calls -> docs/_api_demo_transcripts.md
```

`06_api_integration_demo.py` requires `GEMINI_API_KEY` in `.env` (never
committed — see `.env.example`). Free key from
[aistudio.google.com/apikey](https://aistudio.google.com/apikey). The Chroma
index persists to `data/chroma_db/` (gitignored, regenerable by re-running
`04_setup_vector_db.py`).

After the 4 fixed test cases, `06_api_integration_demo.py` drops into a
**live query loop** — type your own questions about TPC's BSIS program and
get real grounded answers on the spot (`quit`/`exit`/empty line to stop).

## Running the Checkpoint 3 pipeline

```bash
python3 src/07_ingest_pipeline.py    # one-command ingestion: extract -> clean -> chunk -> embed -> index
python3 src/08_rag_app.py            # live multi-turn chat (type 'quit'/'exit'/empty line to stop)
python3 src/08_rag_app.py --demo     # runs the scripted 6-turn demo -> docs/_rag_app_demo_transcripts.md
python3 src/09_llamaindex_comparison.py  # comparison-only LlamaIndex demo, backs Framework_Comparison_Note.md
```

`07_ingest_pipeline.py` is the CP3 "ingestion pipeline" deliverable — it
orchestrates the existing extract/clean/chunk/embed/index stages (no new
pipeline logic, pure reuse) so a new document dropped into `data/raw/` is
fully re-indexed with one command.

`08_rag_app.py` is the CP3 "working application": LangChain
(`langchain-chroma` + `langchain-google-genai`) orchestrating retrieval
against the existing Chroma index, grounded with the `live_advisor` prompt
from `src/prompts.py`, with real conversational memory — a follow-up like
"How many units is it?" is condensed into a standalone query using the prior
turn before retrieval runs, so context actually carries across turns. Both
require `GEMINI_API_KEY` in `.env`.

`09_llamaindex_comparison.py` is comparison-only, not used in production —
see [docs/Framework_Comparison_Note.md](docs/Framework_Comparison_Note.md)
for why LangChain was chosen for the app and what the LlamaIndex demo showed.

## Team

Working in a team of 2–4 (see [docs/Project_Proposal.docx](docs/Project_Proposal.docx)
for the division-of-labor table — placeholder names until finalized). Each
teammate owns one pipeline component: data/embeddings, RAG/orchestration, or
interface/deployment, per the guide's Section 4 requirement.
