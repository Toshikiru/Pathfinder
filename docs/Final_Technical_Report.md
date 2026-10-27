# Pathfinder: A RAG-based Academic Advisor for Course Planning
**Final Technical Report — IS Professional Elective #4 (Generative AI Systems)**
Talibon Polytechnic College · 1st Semester, A.Y. 2026–2027 · Instructor: Jessie A. Melendres
Team: **[FILL IN — names and components, per the Proposal's division-of-labor table]**
Repository: https://github.com/keivautier2428/Pathfinder-A-RAG-based-Academic-Advisor-for-Course-Planning
Live demo: **[FILL IN — public Space URL]**

## 1. Problem and goal

BSIS students at TPC plan course loads by cross-referencing a printed curriculum checklist and asking the
Program Head or Registrar for anything else (prerequisites, probation unit caps, Latin-honors GWA).
That does not scale and is unavailable outside office hours. Pathfinder is a chatbot grounded in TPC's
BSIS curriculum and policies that gives **cited** answers and **refuses** what it cannot support,
instead of guessing. Success criteria (from the Proposal): correct source citation on ≥90% of demo
queries; retrieval latency < 2 s; ≥5 multi-part questions answered without hallucination; at least one
correct refusal per session; coverage of all four year levels and both policy documents.

## 2. Architecture

```
 raw HTML / .txt ──► extract ──► clean ──► chunk ──► embed (MiniLM) ──► Chroma index
 (data/raw)        (01)        (02)      (04)         (04)               (cosine, 105 chunks)
                                                                              │
 Browser ─► Streamlit UI ─► PathfinderSession (LangChain)                     │
 (app/)      per-visitor      1. condense follow-up using chat history        │
             memory           2. detect year/semester → metadata filter       │
                              3. top-4 similarity search ◄────────────────────┘
                              4. live_advisor prompt + CONTEXT + history ─► Gemini ─► cited answer

 Delivery: Dockerfile (multi-stage, index built at build time) ─► GitHub Actions ─► Hugging Face Space
```

| Layer | Choice |
|---|---|
| Embeddings | `all-MiniLM-L6-v2` (open-source, local, 384-dim) |
| Vector store | Chroma (persistent, `hnsw:space="cosine"`) |
| Orchestration | LangChain (`langchain-chroma`, `langchain-google-genai`); LlamaIndex evaluated only |
| Generator | `gemini-3.5-flash-lite` (hosted) |
| Interface | Streamlit |
| Delivery | Docker (multi-stage), GitHub Actions, Hugging Face Spaces |

## 3. Data pipeline (CILO 1)

The corpus is **23 documents → 105 chunks**: 10 real pages scraped from tpc.edu.ph, 8 real files
transcribed from TPC's official BSIS curriculum checklist (A.Y. 2024–2025), and 5 **simulated** files
(course descriptions and two policy documents) built because the student handbook is not public.
Simulated files carry a `[SIMULATED DATA]` label and the app's sidebar warns users of this
(`docs/Data_Sources.md`).

* **Extraction (01):** BeautifulSoup replaced a first-pass regex tag-stripper that leaked inline
  JavaScript into the text.
* **Cleaning (02):** removed ~35 lines of repeated site chrome per page, normalized whitespace, and
  patched an obfuscated registrar e-mail; total size fell ~28% (60,066 → 43,323 characters) without
  losing advising content.
* **Chunking (04):** sentence-aware, ≤500 characters, never splitting a sentence. An earlier
  line-based chunker separated "Latin honors" from its "GWA 1.75" clause and hurt retrieval.
* **Metadata:** every chunk stores `source`, `category`, `chunk_id`; curriculum chunks also store
  `year` and `semester` (used for filtering, §5).
* **Ingestion (07):** one command re-runs extract → clean → chunk → embed → index.

## 4. Prompt design (CILO 2)

Four single-purpose prompts (grounded advisor, prerequisite verifier, scope guard, clarification) were
designed and tested in Checkpoint 2, then merged into one **`live_advisor`** prompt because a live
assistant must handle every case at once. Its ordered rules: (1) refuse off-topic questions in one
sentence; (2) answer only from CONTEXT and otherwise say *"I don't have that information in my
knowledge base"*, never inventing course codes or unit counts; (3) ask a clarifying question when the
answer depends on an unstated year/semester; (4) name the source document; (5) stay concise.
Full rationale and real transcripts: `docs/Prompt_Engineering.md`.

## 5. RAG implementation (CILO 2)

**Distance metric.** We compared cosine, Euclidean, and dot product on our own chunks. All three
returned identical top-3 rankings because MiniLM outputs unit-norm vectors (for unit vectors,
‖a−b‖² = 2 − 2·cos(a,b), and dot product equals cosine). We kept **cosine** because it is the metric the
model was trained for and cannot silently break if a non-normalizing model is swapped in later
(`docs/Distance_Metric_Comparison.md`).

**Framework choice.** LangChain was used for production because it composes with our existing Chroma
index; LlamaIndex wants to own ingestion and re-chunk everything. Both answered our 5 comparison
queries identically once chunking was fixed, so the decision was architectural, not accuracy-based
(`docs/Framework_Comparison_Note.md`).

**Conversational memory.** A message list plus a "condense" LLM call: before retrieval, the latest
question is rewritten into a standalone one using the history ("How many units is it?" → "How many
units is IS 104 System Analysis & Design?"). The standalone question is also used for generation, which
avoids the model asking for clarification when the pronoun has already been resolved.

**Metadata filtering.** All eight curriculum term files share nearly identical headers, so embeddings
alone could not reliably tell "Year 1 Sem 1" from "Year 3 Sem 2". When the question names both a
year and a semester, retrieval is filtered by `year`/`semester` metadata instead of relying on
similarity.

## 6. Interface, containerization and deployment (CILO 4)

* **Interface (`app/streamlit_app.py`):** a chat UI wrapping `PathfinderSession` unchanged. One
  session (and memory) per visitor; the index, embedder and LLM client load once per process; a
  collapsible "Sources & retrieval details" panel shows retrieved documents, the memory-resolved
  query and any metadata filter; example-question buttons; a "New conversation" reset.
* **Containerization (`Dockerfile`):** two stages. The builder installs CPU-only PyTorch and the
  runtime dependencies, downloads the embedding model, and builds the Chroma index. The runtime stage
  copies only the venv, model cache, finished index and code, runs as a non-root user, loads the
  embedder offline, and defines a health check. Final image size: **[FILL IN from `docker images`]**.
* **Secrets:** `GEMINI_API_KEY` is injected at run time only (never in the image, repo or CI); `.env`
  is ignored by Git and Docker; git history contains no keys; see `docs/Deployment_Guide.md`.
* **Abuse and quota protection:** per-session turn cap (30) and question-length cap (500 characters),
  important because the public URL spends a free-tier API quota.
* **CI/CD (`.github/workflows/ci-cd.yml`):** every push/PR builds the image, runs offline smoke tests
  inside it (term detection, index populated, policy retrieval, metadata filter) and checks that the
  container becomes healthy. Pushes to `main` that pass deploy to a Hugging Face Space.
* **Deployment evidence:** URL, screenshots and run recording — **[FILL IN / attach]**.

## 7. Evaluation

Eight-turn scripted conversation (`src/08_rag_app.py --demo`; transcripts in
`docs/_rag_app_demo_transcripts.md`):

| # | Question | Outcome |
|---|---|---|
| 1 | Prerequisites for IS 104? | ✅ IS 103, cited `04_year_2_second_semester.txt` |
| 2 | "How many units is it?" (follow-up) | ⚠️ Memory resolved the question correctly, but retrieval missed the unit count → *"I don't have that information"* (safe failure, not a hallucination) |
| 3 | GWA for Latin honors? | ✅ 1.75 or better, no grade below 2.5, no 5.00 — cited policy file |
| 4 | "Write me a haiku about databases" | ✅ Correct out-of-scope refusal |
| 5 | "What about CC 105?" (follow-up) | ✅ IPT 101 and CC 104 |
| 6 | Units on academic probation? | ✅ 15 units per regular semester |
| 7 | Subjects in first year first sem? | ✅ 10 courses, metadata filter applied |
| 8 | "What about second sem?" (follow-up) | ✅ 8 courses, filter resolved to Year 1 Sem 2 |

**Against the success criteria:** 6 of 8 turns were answered with a correct, cited, grounded answer;
turn 4 was a correct refusal; turn 2 was a safe "don't know" caused by retrieval. The three
follow-up turns (2, 5, 8) show memory working. Year levels 1–3 appear in the demo; **Year 4 should be
added to the live demo set** to fully meet the coverage criterion. Retrieval latency measured with
`tests/measure_retrieval_latency.py`: **[FILL IN mean / p95 / max]** (target < 2 s). We did not build an
automated answer-quality benchmark; the numbers above come from a small scripted set and should be read
as evidence of behaviour, not statistical accuracy.

## 8. Model customization (CILO 3)

No fine-tuning was performed. The generator is a hosted model whose weights are not accessible, our
observed failures are retrieval failures rather than behaviour failures, and curriculum facts change
and belong in the knowledge base rather than in weights. The most promising experiment is contrastive
fine-tuning of the MiniLM embedder (optionally with a LoRA adapter) on question–chunk pairs, evaluated by
recall@4; a QLoRA-tuned open-weight generator would only be for output-format reliability
(`docs/Model_Customization_Note.md`).

## 9. Limitations

1. **Retrieval coverage.** Top-4 retrieval can miss the single chunk holding a fact (turn 2's unit
   count; the "Program Head" query in Checkpoint 3). Larger k, hybrid keyword + vector search, or a
   reranker would help.
2. **Simulated policies.** Five of 23 documents are simulated, so policy answers are not authoritative.
3. **Filter is rule-based.** Year/semester filtering triggers only when both are named explicitly.
4. **Hosted dependency.** Availability and quota depend on the Gemini free tier; the app degrades to a
   friendly error message.
5. **No student records.** The assistant cannot know what a student has already passed, so it cannot
   check an individual's eligibility, only explain the rules.
6. **Scaling.** At ~100× the corpus, embedding at build time and brute-force prompt context would stay
   fine, but retrieval quality (near-duplicate chunks) would degrade first; the in-process Chroma
   store would also need to become a server or managed vector DB.
7. **Small, scripted evaluation** (see §7).

## 10. Lessons learned

* "Strip the tags" is not the same as "understand the markup" — a real HTML parser mattered.
* Chunk boundaries affected retrieval more than the distance metric did.
* When embeddings can't separate near-duplicate documents, structured metadata is the better tool.
* Reporting failures honestly (turn 2) is more defensible than a curated demo.
* Containerizing forced decisions that local runs hide: where the index is built, how the model is
  cached, who owns which files, and how secrets arrive.

## 11. Reproducing the project

```bash
git clone https://github.com/keivautier2428/Pathfinder-A-RAG-based-Academic-Advisor-for-Course-Planning
cd Pathfinder-A-RAG-based-Academic-Advisor-for-Course-Planning
docker build -t pathfinder .
docker run --rm -p 7860:7860 -e GEMINI_API_KEY=<your-key> pathfinder     # http://localhost:7860
```

*AI-assistance disclosure: **[FILL IN — the course guide requires citing AI-assisted code/documentation, e.g. the Checkpoint 4 interface, Dockerfile, CI workflow and documentation drafts.]***
