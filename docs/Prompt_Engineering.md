# Prompt Engineering Document

Four structured system/instruction prompts, defined in [`src/prompts.py`](../src/prompts.py)
and exercised for real via [`src/06_api_integration_demo.py`](../src/06_api_integration_demo.py)
against the Gemini API (`gemini-3.6-flash`), grounded in context retrieved from
the Chroma index. **Every transcript quoted below is a real model output**,
captured in [`docs/_api_demo_transcripts.md`](_api_demo_transcripts.md) — none
of these are hand-written/simulated examples.

---

## 1. `grounded_advisor` — general grounded Q&A

**Purpose:** the default prompt for factual course/policy questions. Forces
the model to answer only from retrieved CONTEXT, cite the source document,
and explicitly say "I don't have that information" rather than filling gaps
with outside knowledge — the core anti-hallucination guardrail for this
project (rubric requirement: "demonstrably reduce hallucination/off-scope
answers").

**Design choices:**
- Rule 1 forbids outside knowledge about "universities, curricula, or
  policies in general" specifically, because a general-purpose LLM *does*
  know a lot about typical university structures and would otherwise
  plausibly fill in gaps with generic (wrong-for-TPC) assumptions.
- Rule 2 gives the model an explicit, literal fallback sentence to say
  instead of guessing — models are far less likely to hallucinate when given
  a concrete "safe" thing to say instead.
- Rule 3 requires source attribution so a student can verify the claim, not
  just trust it.

**Example (real transcript):** *"What are the prerequisites for IS301
Systems Analysis and Design, and how many units is it?"*

> Per the Year 3 - First Semester curriculum checklist
> (`curriculum/05_year_3_first_semester.txt`), the prerequisites for
> **IS301 Systems Analysis and Design** are:
> * **IS201** (Data Structures and Algorithms)
> * **IS205** (Information Management 1)
>
> Regarding how many units the course is worth, I don't have that
> information in my knowledge base.

Note the second half: the retrieved chunk *did* contain "IS301 ... 3 ..." in
a table row, but the model treated the unit count as not confidently
extractable from the chunk boundary it saw and declined rather than
guessing. That's the rule working — arguably over-cautious here, but the
failure mode we designed against (confidently inventing a unit count) did
not happen. This is a concrete data point for Checkpoint 3: tighter
chunking (so a full table row never gets split) should improve completeness
without touching the prompt.

---

## 2. `prerequisite_verifier` — structured prerequisite-chain checking

**Purpose:** prerequisite questions are exactly where an LLM is most tempted
to hallucinate, because "Course X requires Course Y" is a *very* plausible-
sounding sentence to generate even when false. This prompt forces a rigid
output structure (Course / Prerequisites found / Confidence) so a wrong or
missing answer is visually obvious rather than buried in prose.

**Design choices:**
- The Confidence field is binary and literal ("Confirmed from context" /
  "Not found in provided context") rather than open-ended, so the model
  can't hedge with vague confidence language that still implies an answer.
- Rule 4 explicitly forbids "reasonable assumption about typical curricula"
  — anticipating that a model might reason "well, IS301 is a systems course,
  it probably needs Data Structures" even without that being in context.

**Example (real transcript) — hallucination trap:** the corpus was queried
with a course code that does not exist anywhere in the 30-document knowledge
base: *"What are the prerequisites for IS999 Advanced Quantum Computing for
Business?"*

> - Course: IS999 - Advanced Quantum Computing for Business
> - Prerequisite(s) found in context: None found
> - Confidence: Not found in provided context
>
> The course code IS999 was not located in the knowledge base.

The model correctly refused to invent a prerequisite chain for a
nonexistent course, even though the retrieved context (4 real curriculum
chunks) contained plenty of *real* prerequisite relationships it could have
pattern-matched from.

---

## 3. `scope_guard` — out-of-scope refusal

**Purpose:** prevents the assistant from answering questions unrelated to
TPC/BSIS advising — required so the bot doesn't become a general-purpose
chatbot that happens to also know about course planning, which would dilute
trust in its advising answers and is explicitly called out in the guide's
"failure/out-of-scope case handled gracefully" rubric line.

**Design choices:** the refusal message is deliberately short and offers a
redirect back into scope, rather than a long apology — a one-line decline
reads as a confident, intentional boundary rather than the model being
"stuck."

**Example (real transcript):** *"Can you write me a 4-line poem about cats,
and also what's the capital of France?"*

> That's outside what I can help with — I am scoped strictly to TPC BSIS
> course planning, enrollment, and academic-standing questions. Is there
> something about your BSIS curriculum or degree progress I can help with
> instead?

Correctly declined both the creative-writing request and the general-trivia
question in one pass, without answering either.

---

## 4. `clarification` — ambiguity handling

**Purpose:** a distinct failure mode from hallucination: the model *could*
answer confidently by silently picking one of the 9 terms in the corpus and
presenting it as "the" answer, which would be wrong for most students asking
a term-dependent question without saying which term they mean. This prompt
makes the assistant recognize when a question is underspecified and ask
before answering, instead of retrieving whichever term happens to rank
highest and presenting it as universal.

**Example (real transcript):** *"What subjects should I take next
semester?"* — no year, semester, or completed-courses information given.

> Which year and semester are you currently in, or which courses have you
> already completed? Once you share your current standing, I can give you
> the exact list of subjects you should take next semester.

The retrieved context (via semantic search) happened to include Year 2 Sem 2
and Year 4 Sem 2 curriculum chunks — a naive grounded-answer prompt would
likely have picked one and answered as if it applied universally. This
prompt caught the ambiguity instead.

---

## Summary

| Prompt | Guards against | Verified via |
|---|---|---|
| `grounded_advisor` | Hallucinating facts not in the KB | Real answer + correct citation |
| `prerequisite_verifier` | Inventing plausible-but-false prerequisite chains | Real refusal on a fabricated course code |
| `scope_guard` | Answering off-topic requests | Real refusal on an unrelated question |
| `clarification` | Confidently answering an underspecified question | Real clarifying question instead of a guess |
