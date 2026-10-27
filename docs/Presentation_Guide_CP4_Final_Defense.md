# Final Presentation & Defense Guide (Checkpoint 4)

**Format (from the project guide):** 10–15 min presentation + 5–10 min Q&A · live demo required ·
backup recording ready · **every member speaks and must be able to answer about any component.**

## 1. Run of show (≈ 13 minutes)

| Min | Slide / action | Say (plain language) | Suggested speaker* |
|---|---|---|---|
| 0:00–1:30 | **1. Problem** | Students plan courses from a paper checklist and wait for office hours. Pathfinder answers prerequisite and policy questions instantly, with sources. | Member 1 |
| 1:30–4:00 | **2. Architecture** (one diagram: data → embeddings → Chroma → LangChain RAG → Streamlit → Docker/CI → HF Space) | Walk the diagram left to right. Mention 23 docs → 105 chunks, MiniLM, cosine, top-4, Gemini, memory. | Member 2 |
| 4:00–8:00 | **3. LIVE DEMO** of the deployed URL | See §2. | Member 3 drives, others narrate |
| 8:00–10:30 | **4. Key decisions** | Cosine (all metrics tie because vectors are unit-norm); LangChain over LlamaIndex (reuse our index); metadata filter for near-duplicate term files; no fine-tuning, and why. | Member 2 / 1 |
| 10:30–12:00 | **5. Deployment** | Multi-stage Docker, index built at build time, secret injected at runtime, GitHub Actions → HF Space. Show the green run. | Member 3 |
| 12:00–13:00 | **6. Limitations & next steps** | Retrieval misses, simulated policies, quota. Next: hybrid search, reranker, fine-tuned embedder. | Member 1 |

\*Placeholder split — assign by who owns which pipeline component in your Proposal.

## 2. Demo script (use the deployed URL, not localhost)

Start a **New conversation**, then ask, in order:

1. *What are the prerequisites for IS 104 System Analysis & Design?* → grounded answer; open **Sources & retrieval details**.
2. *How many units is it?* → shows memory (watch the "standalone query"). *If it answers "I don't have that information", that is a known retrieval miss — say so and explain it's the safe failure mode; do not hide it.*
3. *What's the GWA requirement for Latin honors?* → policy retrieval.
4. *Can you write me a haiku about databases?* → **required out-of-scope refusal**.
5. *What subjects are in first year first semester?* then *What about second sem?* → metadata filter + memory.
6. *What subjects are in fourth year second semester?* → covers **Year 4** (the one year level missing from the earlier demo set).

Pre-flight checklist: open the URL 5 minutes early (free Spaces sleep); test once with the real key;
keep the 1–2 minute screen recording ready; have `docker run …` ready in a terminal as plan C;
note your Gemini quota (a free-tier limit has been hit before in this project's history).

## 3. Likely defense questions — answers grounded in this project

**Why this distance metric / vector DB?**
We ran cosine, Euclidean and dot product on our own 105 chunks; rankings were identical because
all-MiniLM-L6-v2 outputs unit-length vectors (‖a−b‖² = 2 − 2cos, and dot = cos). We kept cosine because
it is the metric the model was trained for and can't silently break if we swap in a non-normalized
model. Chroma: embedded/persistent, no server to run, supports metadata filters, free — right-sized
for 105 chunks.

**Walk us through what happens when a user submits a query.**
UI → if there's chat history, one LLM call rewrites the question to be standalone → regex detects a
named year + semester → Chroma top-4 cosine search (filtered by metadata if a term was named) →
chunks formatted into CONTEXT → `live_advisor` system prompt + history + CONTEXT + question → Gemini →
answer with source filename → shown with the retrieved sources → saved to session memory.

**How does the system avoid hallucination?**
Four layers: (1) the prompt restricts answers to CONTEXT and mandates "I don't have that information…"
and forbids inventing codes/units; (2) retrieval returns only our documents; (3) sources are displayed so
users can verify; (4) a scope rule refuses off-topic questions. Evidence: turn 4 (haiku refused) and turn 2
(unknown → says so rather than guessing).

**What would break first at 100× the documents?**
Retrieval quality: more near-duplicate chunks means the right chunk drops out of top-4 (we already see
this with curriculum headers). Fixes: hybrid BM25 + vector search, reranking, richer metadata, larger k.
Infrastructure comes second: the in-process Chroma store would move to a server/managed DB, and
build-time indexing to an incremental ingestion job.

**If you fine-tuned with LoRA/QLoRA, what would you target?**
First the embedder (contrastive fine-tuning on question→chunk pairs, measured by recall@4), because our
failures are retrieval failures. A QLoRA open-weight generator would only be for output-format
consistency. Facts stay in retrieval because they change every curriculum revision. (`Model_Customization_Note.md`)

**Why didn't you fine-tune?** Hosted generator (no weights), failures are retrieval-side, facts change,
tiny and partly simulated data, free CPU deployment target.

**Is it secure?** Key injected at runtime only, never in image/repo/CI; non-root container; telemetry off;
per-session turn and length caps; git history scanned for keys; revoke-and-rotate policy if leaked.
Honest limits: no user authentication, and the public URL spends a shared free-tier quota.

**Why multi-stage Docker?** Build-time work (pip, model download, indexing) stays in the builder; the
runtime image only has what it needs, and starts instantly without downloading the model.

**How do you know the answers are right?** Small scripted evaluation (8 turns; 6 correct cited answers,
1 correct refusal, 1 safe "don't know") plus offline smoke tests in CI. We have no large automated
benchmark — say so; proposing a held-out question set is the first improvement.

**Which data is real?** 18 of 23 documents are real (website + official checklist); 5 are simulated and
labeled, and the UI warns about it.

**What did *you* personally build?** Each member should prepare 2–3 sentences on their own component
(data & embeddings / RAG & prompting / interface & deployment) **and** be able to explain one other
component — graders will ask across components.
