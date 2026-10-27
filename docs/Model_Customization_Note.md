# Model Customization Note — PEFT (LoRA/QLoRA) for Pathfinder

**Checkpoint 4, Deliverable 15.** *Decision: no fine-tuning was performed. Pathfinder uses an
instruction-tuned hosted model (`gemini-3.5-flash-lite`) and an open-source embedding model
(`all-MiniLM-L6-v2`) as-is. This note explains why, and exactly what we would fine-tune if we did.*

## 1. What each model does, and whether it can be customized

| Component | Model | Weights accessible? | PEFT applicable? |
|---|---|---|---|
| Generator (writes the answer) | `gemini-3.5-flash-lite` via API | No (hosted, proprietary) | No — we can only prompt it |
| Embedder (finds the chunks) | `sentence-transformers/all-MiniLM-L6-v2`, 384-dim, open-source | Yes | Yes |

This matters for CILO 3: the generator is a hosted API, so LoRA/QLoRA cannot be applied to it. Any
generator fine-tuning would mean *swapping* it for an open-weight model (Section 4).

## 2. Why base/instruction-tuned models were the right call for this release

1. **The knowledge changes; weights shouldn't.** Curricula are revised (our checklist is effective
   A.Y. 2024–2025 and will be superseded), and policy numbers such as the 15-unit probation cap can
   change. With RAG, updating an answer means editing a text file and re-running
   `src/07_ingest_pipeline.py`. With fine-tuning it would mean re-training, and a fine-tuned model can
   still confidently recite the *old* value. Fine-tuning is poor at storing precise, changing facts;
   retrieval is built for them.
2. **Our observed failures are retrieval/data failures, not model-behaviour failures.** In the
   Checkpoint 3 transcripts (`docs/_rag_app_demo_transcripts.md`) the model followed its rules
   correctly: it cited sources, refused the haiku request, and said "I don't have that information"
   when the retrieved context lacked the answer. The misses ("How many units is IS 104?", the
   Program Head query) happened because the right chunk was not in the top-4 retrieved — fixing the
   *generator* would not have fixed them.
3. **Prompt + metadata filtering already solved the behaviour problems we could measure.** The
   `live_advisor` prompt handles scope refusal, grounding and clarifying questions
   (`docs/Prompt_Engineering.md`), and the year/semester metadata filter fixed near-duplicate
   curriculum headers (Checkpoint 3). Both are cheaper and easier to audit than training.
4. **Data volume.** The corpus is 23 documents / 105 chunks, and 5 of the 23 documents are
   simulated. Training on that — or on question/answer pairs synthesized from it — risks the model
   memorizing our simulated policies as if they were TPC's real ones.
5. **Cost and reproducibility.** The whole system runs on CPU in a free-tier container. A fine-tuned
   generator would need GPU hosting or a quantized CPU build, which does not fit the free deployment
   target.

## 3. Where PEFT would help most: the embedder (recommended first experiment)

The most valuable customization target is **retrieval**, because that is where our measured
failures come from.

* **Problem:** every curriculum term file shares near-identical header/table boilerplate, so general
  purpose MiniLM struggles to separate "Year 1 Sem 1" from "Year 3 Sem 2" (we patched this with
  metadata filtering, which only works when the user names year *and* semester explicitly). Course
  codes (`IS 104`, `CC 105`) are also weak signals for a general sentence-embedding model.
* **Approach:** fine-tune MiniLM contrastively (e.g. `MultipleNegativesRankingLoss` in
  sentence-transformers) on (question, correct chunk) pairs. MiniLM is only ~22M parameters, so full
  fine-tuning fits on a laptop CPU/free Colab; a LoRA adapter (via the `peft` library) is optional
  here and mainly reduces what must be stored per experiment.
* **Data:** ~300–500 pairs, generated from the curriculum files (each course row → "What are the
  prerequisites for X?" / "How many units is X?") and **manually spot-checked**; hold out ~20% as an
  evaluation set.
* **Success metric:** recall@4 on the held-out set versus the untouched baseline model, plus
  re-running the eight scripted demo turns. We would adopt the adapter only if recall@4 improves
  meaningfully with no regression on policy/website queries.

## 4. If we did fine-tune a generator: QLoRA on an open-weight model

*Goal would be style/format reliability (always cite a source file, use the exact refusal phrasing,
ask the clarifying question) — not storing facts.*

* **Base model:** a small instruction-tuned open-weight model (roughly 1–3B parameters, e.g.
  Qwen2.5-3B-Instruct or Llama-3.2-3B-Instruct) so it can run on a free Colab T4 (16 GB).
* **QLoRA recipe:** load the base in 4-bit NF4 (≈0.5 byte/parameter → roughly 1.5–2 GB of weights for
  3B), attach LoRA adapters (e.g. rank 16 on the attention projections), use gradient checkpointing
  and a small batch with gradient accumulation. LoRA trains ΔW = B·A with rank r ≪ d, so only about
  2·r·d parameters per adapted matrix are updated — tens of MB of adapter instead of the full model.
  *(Sizes are back-of-envelope estimates, not measurements from this project.)*
* **Training data:** (system prompt + retrieved CONTEXT + question → ideal answer) triples, including
  deliberate negatives (context lacks the answer → exact "I don't have that information…" reply;
  off-topic question → scope refusal). Because the context is in the prompt, the model learns *behaviour*,
  and facts still come from retrieval.
* **Risks we would have to manage:** overfitting to a tiny dataset; the model learning the wrong
  refusal boundary; loss of general capability; and an adapter that must be re-validated every time
  the prompt format changes.

## 5. Conclusion

Using the models as-is was a deliberate, evidence-based decision: our failures were retrieval- and
data-related, the knowledge is time-sensitive (a poor fit for weight updates), and the generator is not
open-weight. If we continue the project, the first experiment is contrastive fine-tuning of the
embedder with a held-out recall@4 evaluation; generator QLoRA would come only after that, and only
to harden output format.
