# Framework Comparison Note — LangChain vs. LlamaIndex

**Method:** both frameworks were actually run against our own corpus, not
compared on paper. `src/08_rag_app.py` (LangChain, production) and
`src/09_llamaindex_comparison.py` (LlamaIndex, comparison-only) are real,
runnable scripts; every number and quote below is real output, not a
hand-written example — consistent with how this project documented the
distance-metric comparison in Checkpoint 2
([docs/Distance_Metric_Comparison.md](Distance_Metric_Comparison.md)).

## Which parts of each we used, and why

| | LangChain (`08_rag_app.py`) | LlamaIndex (`09_llamaindex_comparison.py`) |
|---|---|---|
| Role | **Production RAG app** | Comparison demo only — not wired into the app |
| Data routing | Manual: our own retriever call -> our own prompt template -> LLM (LCEL-style composition, no chain-constructor helpers) | `VectorStoreIndex.from_documents()` + `.as_query_engine()` — one call owns node-parsing, embedding, indexing, and querying |
| Node/chunk indexing | Reused the **existing** `pathfinder_bsis_advisor` Chroma collection built by `04_setup_vector_db.py`'s hand-rolled, sentence-aware chunker | Its own `SimpleDirectoryReader` + `SentenceSplitter` (token-based, `chunk_size=128` tokens) into a **separate** Chroma collection (`pathfinder_llamaindex_demo`) — LlamaIndex wants to own ingestion end-to-end, not consume an index built by someone else |
| Memory | Hand-rolled: a message list + a "condense the follow-up into a standalone question" LLM call before each retrieval, and that same standalone question is reused for answer generation too (see below) | Not used here (`as_query_engine()` is single-turn); LlamaIndex does offer `as_chat_engine()` with built-in condense-question memory, conceptually the same idea we hand-rolled |

**Why LangChain for production:** it let us keep our own chunking approach
and layer orchestration + memory on top without re-indexing anything.
LlamaIndex's `VectorStoreIndex` is opinionated about owning the ingestion
pipeline itself — using it for production would have meant re-chunking
everything under its own `SentenceSplitter`. On this corpus, after this
checkpoint's chunking fix, both approaches now answer equivalently (see
below) — so the deciding factor wasn't retrieval accuracy, it was
architectural fit: LangChain's lower-level primitives compose directly with
an index we already control, and hand-rolling the condense-question memory
step ourselves (rather than adopting a chain-constructor helper) kept the
app decoupled from any one LangChain chain API.

## Real output, side by side

Both systems were run against the same 5 queries over the same (real BSIS
curriculum + TPC website + policy) corpus:

| Query | LangChain answer | LlamaIndex answer |
|---|---|---|
| Prerequisites for IS 104 System Analysis & Design? | IS 103 (IT Infrastructures and Network) | IS 103 (IT Infrastructures and Network) |
| Units on academic probation? | Capped at 15 units per regular semester | Capped at 15 units per regular semester |
| Program head of BSIS? | Not found in retrieved context | Not found in retrieved context |
| Required to enroll in Capstone Project I? | 3rd Year Standing | 3rd Year Standing |
| GWA for Latin honors? | Cumulative GWA of 1.75 or better | Cumulative GWA of 1.75 or better |

**All 5 answers agree.** That's a meaningfully different result from
earlier in this checkpoint, when LlamaIndex's default chunker split a
curriculum-checklist row awkwardly and gave an *incomplete* prerequisite
answer that our (then-buggy) hand-rolled chunker's index didn't. Fixing the
sentence-aware chunking this checkpoint (see `03_generate_embeddings.py` /
`04_setup_vector_db.py`) closed that gap on both sides — LlamaIndex's
default `SentenceSplitter` and our chunker now both keep prerequisite rows
intact on this corpus. The "program head" query fails identically in both
(the name lives in a chunk neither system's top-k retrieval surfaces for
that phrasing) — a retrieval-coverage limitation independent of framework
choice, not a chunking issue.

**Honest implication:** on *this* corpus, framework choice didn't move
answer accuracy. The case for LangChain in production is architectural
(reusing our own index/prompts, and controlling exactly how memory works)
rather than an accuracy argument — which is a more defensible reason to
choose a framework than "it happened to get one more answer right in a
5-query sample," and matches this project's practice of reporting what
actually happened rather than what would make the best story.

## Recommendation

**LangChain for the working application, LlamaIndex evaluated and not
adopted for production** — not because LlamaIndex performed worse (it
didn't, once chunking was fixed), but because its ingestion-owning design
doesn't compose with an already-built, already-tuned index the way
LangChain's lower-level retriever/LLM primitives do. If a future checkpoint
needed LlamaIndex's strengths specifically — its query-engine/chat-engine
abstractions, or routing across multiple indices/data sources — it would be
worth re-evaluating with our chunker plugged into a custom LlamaIndex
`VectorStoreIndex` built from pre-chunked nodes rather than letting it
re-chunk from scratch.
