# Distance Metric Comparison — Cosine vs. Euclidean vs. Dot Product

**Method:** `src/05_distance_metric_comparison.py` embeds all 109 chunks of
our own processed corpus with `all-MiniLM-L6-v2`, then runs the same 4
realistic advising queries against the same embedding matrix under three
scoring functions computed by hand (not via a library default), so the
comparison is apples-to-apples on our own data:

- **Cosine similarity:** `(a · b) / (‖a‖ ‖b‖)` — higher is better.
- **Euclidean (L2) distance:** `‖a − b‖` — lower is better.
- **Dot product:** `a · b`, using the **unnormalized** raw embeddings — higher is better.

## Result: the three metrics produced identical rankings on every query

For all 4 test queries (prerequisites lookup, policy lookup, entity lookup,
GWA lookup), Cosine, Euclidean, and Dot Product returned the exact same
top-3 documents in the exact same order. Full output: run the script, or
see `docs/_distance_metric_results.json`.

**Why, concretely:** the script printed the embedding norm range before
scoring — `Norm range: 1.000 - 1.000` — even though embeddings were
generated with `normalize_embeddings=False`. `all-MiniLM-L6-v2`'s published
architecture ends with a built-in `Normalize` layer (see the model's
`modules.json` on Hugging Face), so **every embedding it produces already
has unit L2 norm, regardless of any flag passed at encode time.** That has
two direct mathematical consequences on this corpus:

1. **Dot product ≡ Cosine** when every vector has norm 1, because
   `cosine(a,b) = (a·b)/(‖a‖‖b‖) = (a·b)/(1·1) = a·b`. There is no
   daylight between the two for this model family, no matter what data we
   feed it.
2. **Euclidean distance is a monotonic transform of cosine** for unit
   vectors: `‖a−b‖² = ‖a‖² + ‖b‖² − 2(a·b) = 2 − 2·cos(a,b)`. Ranking by
   ascending Euclidean distance is mathematically guaranteed to produce the
   same order as ranking by descending cosine similarity — which is exactly
   what we observed.

## Recommendation

**Use Cosine similarity** (already configured as `hnsw:space="cosine"` in
`src/04_setup_vector_db.py`'s Chroma collection). Reasoning:

- For this embedding model, cosine, dot product, and Euclidean are
  mathematically equivalent in ranking outcome — so correctness is not the
  deciding factor, semantic clarity and future-proofing are.
- Cosine is the metric `all-MiniLM-L6-v2` was **trained against** (it's a
  sentence-similarity model optimized with a cosine-based objective), so
  it's the metric whose *scale* is most interpretable: a cosine score of
  0.85 means something consistent, whereas a raw dot-product magnitude
  would silently become misleading if a future embedding model swap
  (Checkpoint 3/4) does **not** normalize its output the way MiniLM does.
- If we ever mix in an embedding model that does *not* L2-normalize by
  default, dot product would start rewarding longer/higher-magnitude
  chunks regardless of semantic relevance — a subtle bug. Standardizing on
  cosine now means that failure mode can't creep in silently later.

**One caveat worth flagging for Checkpoint 3:** because the metrics tie out
identically here, this comparison alone doesn't prove cosine is *better* —
it proves the three are indistinguishable *for this specific model*. The
real lever for retrieval quality on this corpus turned out to be **chunk
size**, not distance metric (see `docs/Reflection_Checkpoint1.md`'s note
about the "program head" query, and Checkpoint 2's demo output where a
whole-document chunk sometimes outranks a more specific one). That's the
next thing to tune, not the metric.
