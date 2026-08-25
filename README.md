# Pathfinder: A RAG-based Academic Advisor for Course Planning and Degree Progress

Mini Generative AI Capstone Project — IS Professional Elective #4 (Generative AI Systems)
Talibon Polytechnic College · 1st Semester, A.Y. 2026–2027 · Instructor: Jessie A. Melendres

**Theme:** Document/Knowledge-Base Q&A Assistant, specialized for academic advising —
a RAG chatbot grounded in TPC's BSIS curriculum, course prerequisites, and academic
policies, so students can ask course-planning and degree-progress questions and get
a cited, non-hallucinated answer instead of manually cross-referencing a checklist.

## Checkpoint status

- [x] **Checkpoint 1 — Foundation & Data Pipeline** (Prelim): proposal, dataset,
      preprocessing, embedding demo. *Complete.*
- [x] **Checkpoint 2 — Prompt Architecture & Vector Indexing** (Midterm): prompt
      engineering doc, Gemini API integration, Chroma vector DB, distance metric
      comparison. *Complete — see below.*
- [ ] Checkpoint 3 — RAG Orchestration & Working Application (Semi-Final)
- [ ] Checkpoint 4 — Customization, Deployment & Final Defense (Final)

## Repository layout

```
data/
  raw/
    tpc_website_html/   16 raw HTML pages scraped from tpc.edu.ph (source of truth)
    tpc_website/        same 16 pages, extracted to plain text (still messy - real "raw" layer)
    curriculum/         12 simulated BSIS curriculum-checklist + course-description docs
    policies/           2 simulated academic-policy docs
  processed/             output of 02_preprocess.py (cleaned text + _manifest.json)
    _embeddings/          output of 03_generate_embeddings.py (sample chunk vectors)
src/
  00_generate_curriculum_data.py   generates the simulated curriculum/policy documents
  01_extract_raw_text.py           HTML -> raw text (BeautifulSoup)
  02_preprocess.py                 raw text -> cleaned text, prints before/after examples
  03_generate_embeddings.py        embedding generation + retrieval sanity check (CP1 sample)
  04_setup_vector_db.py            chunks + embeds the FULL corpus into a persistent Chroma index
  05_distance_metric_comparison.py cosine vs euclidean vs dot product on our own data
  06_api_integration_demo.py       retrieval + system prompts -> real Gemini API calls
  prompts.py                       the 4 structured system/instruction prompts
scripts/
  fill_proposal.py        fills docs/Project_Proposal.docx from the instructor's template
docs/
  Project_Proposal.docx   Checkpoint 1 deliverable
  Data_Sources.md          full provenance of every document in data/raw
  Reflection_Checkpoint1.md
  Prompt_Engineering.md            Checkpoint 2 deliverable (quotes real Gemini transcripts)
  Distance_Metric_Comparison.md    Checkpoint 2 deliverable
  _api_demo_transcripts.md         raw transcripts referenced by Prompt_Engineering.md
  _distance_metric_results.json    raw results referenced by Distance_Metric_Comparison.md
```

## Data sources (summary — full detail in [docs/Data_Sources.md](docs/Data_Sources.md))

30 documents total:
- **16 real**, scraped from TPC's public website (`tpc.edu.ph`): program
  descriptions, admission requirements, enrollment process, registrar/guidance
  services, contact info.
- **14 simulated**, generated from a structured curriculum model based on
  **CHED Memorandum Order No. 25, s. 2015** (the actual national policy
  standard for BSIS programs in the Philippines): a 9-term curriculum
  checklist, course-description catalog, and academic policy documents.
  TPC's real registrar prospectus/handbook is not published online, so this
  gap is filled transparently — every simulated file is labeled
  `[SIMULATED DATA]` in its first line.

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
python3 src/04_setup_vector_db.py            # builds the full 109-chunk Chroma index, runs a similarity-search demo
python3 src/05_distance_metric_comparison.py # cosine/euclidean/dot-product comparison -> docs/_distance_metric_results.json
python3 src/06_api_integration_demo.py       # retrieval + prompts -> real Gemini calls -> docs/_api_demo_transcripts.md
```

`06_api_integration_demo.py` requires `GEMINI_API_KEY` in `.env` (never
committed — see `.env.example`). Free key from
[aistudio.google.com/apikey](https://aistudio.google.com/apikey). The Chroma
index persists to `data/chroma_db/` (gitignored, regenerable by re-running
`04_setup_vector_db.py`).

## Team

Working in a team of 2–4 (see [docs/Project_Proposal.docx](docs/Project_Proposal.docx)
for the division-of-labor table — placeholder names until finalized). Each
teammate owns one pipeline component: data/embeddings, RAG/orchestration, or
interface/deployment, per the guide's Section 4 requirement.
