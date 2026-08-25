# Pathfinder — CP1 & CP2 Presentation Script

Read this like a script. **RUN** = type this command. **SAY** = say this
(your own words are fine, this is just the beat to hit). ~12-15 minutes total.

Before you go on: venv activated, `pip install -r requirements.txt` done,
`.env` has your real Gemini key. Run everything once beforehand so nothing
downloads live. Don't show `.env` on screen.

---

## Open

**SAY:**
> "Pathfinder is a RAG-based academic advisor for TPC's BSIS program. Students
> can ask course-planning and degree-progress questions and get a cited,
> grounded answer instead of digging through a checklist. Checkpoint 1 is the
> data foundation. Checkpoint 2 is prompt design and the vector index."

---

## Checkpoint 1 — Foundation & Data Pipeline

**SHOW:** `docs/Project_Proposal.docx`

**SAY:**
> "Here's the proposal — problem statement, target users, dataset sources,
> success criteria."

**SHOW:** `docs/Data_Sources.md`

**SAY:**
> "30 documents total. 16 are real — scraped from TPC's public website. The
> other 14 don't exist on TPC's site at all. The actual curriculum checklist
> and academic policies live in a 52-page student handbook that's
> preview-locked online — we couldn't get the real text. Instead of quietly
> making up course requirements, we built that half of the dataset from CHED
> Memorandum Order 25, s. 2015 — the real national policy that governs BSIS
> programs in the Philippines. Every simulated file is labeled
> `[SIMULATED DATA]` right in the file."

**RUN:**
```bash
python3 src/00_generate_curriculum_data.py
```
**SAY:** "Generates the CHED-based curriculum and policy docs."

**RUN:**
```bash
python3 src/01_extract_raw_text.py
```
**SAY:**
> "Pulls plain text out of the 16 scraped pages with BeautifulSoup. We
> tried a regex tag-stripper first — it leaked raw JavaScript into the text.
> Switching to a real HTML parser fixed it."

**RUN:**
```bash
python3 src/02_preprocess.py
```
**SAY (while the before/after examples print):**
> "This strips about 35 lines of repeated site-chrome per page — nav, footer,
> a feedback widget — and fixes a broken email placeholder. Cut the corpus
> by roughly 28% with zero loss of actual advising content."

**RUN:**
```bash
python3 src/03_generate_embeddings.py
```
**SAY:**
> "We embed with `all-MiniLM-L6-v2` — open-source, runs fully local, no API
> cost. Watch the bottom of the output: similar questions land close
> together in embedding space, which is the sanity check before wiring up a
> real vector database."

**SHOW:** `docs/Reflection_Checkpoint1.md` — read the last paragraph out loud.

**SAY:**
> "This is where we caught our first real retrieval problem: a broad
> curriculum table was outranking a more specific course description for a
> targeted query, because we were chunking whole documents. That's the
> setup for Checkpoint 2."

*(Quick rubric map if asked where something is graded: proposal + the "16
real / 14 simulated" story = scope clarity. `02_preprocess.py` output =
preprocessing. `03_generate_embeddings.py` = embeddings. README + commit
history = repo hygiene.)*

---

## Checkpoint 2 — Prompts & Vector Indexing

**SAY:**
> "Checkpoint 2 proves two things: we can constrain the model's behavior with
> structured prompts, and we can stand up a real, queryable vector index over
> the whole corpus."

**RUN:**
```bash
python3 src/04_setup_vector_db.py
```
**SAY (point at one result on screen):**
> "This indexes all 30 documents — 109 chunks — into Chroma using cosine
> similarity. Look at the probation query — it pulls the exact policy chunk
> with the 15-unit cap. That's real retrieval, not keyword matching."

**RUN:**
```bash
python3 src/05_distance_metric_comparison.py
```
**SHOW:** `docs/Distance_Metric_Comparison.md`

**SAY:**
> "We compared cosine, Euclidean, and dot product by hand on our own data.
> All three gave identical rankings — because our embedding model has a
> built-in normalization layer, which makes cosine and dot product
> mathematically the same, and Euclidean just a rescaled version of cosine.
> That's a real finding, not a dodge — and we still land on cosine as the
> right default, for reasons the doc lays out."

**SHOW:** `docs/Prompt_Engineering.md` (briefly)

**SAY:**
> "We built 4 structured system prompts, each aimed at one failure mode:
> hallucinating a fact, inventing a fake prerequisite, answering something
> off-topic, and confidently answering a question that's too vague to answer
> safely. Every example in this doc is a real captured transcript — nothing
> here was written by hand."

**RUN — this is the centerpiece:**
```bash
python3 src/06_api_integration_demo.py
```

**SAY while the 4 fixed cases scroll by:**
> "Watch these four go by: a grounded answer with a citation... a refusal to
> invent prerequisites for a course that doesn't exist... a decline on an
> off-topic question... and a clarifying question instead of a guessed
> answer."

Then it drops into **live query mode** — `Your question:` — type a few of
these on the spot:

- `What are the prerequisites for IS205 Information Management 1?`
  — clean grounded answer with a citation
- `How many units can I enroll in while on academic probation?`
  — pulls the exact figure (15 units)
- `What's the weather like today?`
  — off-topic refusal, live and unscripted
- `What subjects should I take next?`
  — asks which year/semester instead of guessing
- `What are the prerequisites for IS777 Blockchain for Farmers?`
  — live hallucination trap, a course made up on the spot

Type `quit` to exit when you're done.

**If the API errors out live (rate limit, network blip):**
**SAY:**
> "This is actually the error handling working as designed — instead of
> crashing, it reports the failure cleanly."

Then retry once, or fall back to `docs/_api_demo_transcripts.md`.

---

## Close

**SAY:**
> "So — Checkpoint 1 gave us a real, honestly-sourced knowledge base.
> Checkpoint 2 gives us grounded, refusal-aware answers over that data, backed
> by a real vector index. Checkpoint 3 turns this into a full RAG application
> with memory and an ingestion pipeline."

---

## If something breaks

- **Chroma index missing/stale** → re-run `python3 src/04_setup_vector_db.py`.
- **`GEMINI_API_KEY not set`** → `.env` still has the placeholder on this
  machine.
- **429 / quota error** → we already standardize on `gemini-3.5-flash-lite`
  because the flagship model's free tier is only 20 requests/day (we hit
  that during dev — it's noted at the top of `Prompt_Engineering.md`). If it
  still happens, that's today's quota on this key — use the saved
  transcripts.
- **A live answer looks thin** → own it: *"that's the chunking limitation
  we flagged in the Checkpoint 1 reflection — it's on the list for
  Checkpoint 3's ingestion pipeline."* Better than pretending it's not there.
