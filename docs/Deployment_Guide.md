# Deployment Guide — Containerization, Secrets & Deployment Evidence

**Checkpoint 4, Deliverables 17 and 18.**

## 1. What the Dockerfile does (multi-stage)

| Stage | Base | Purpose |
|---|---|---|
| `builder` | `python:3.12-slim` | Creates a venv, installs **CPU-only** PyTorch + `requirements-app.txt`, downloads `all-MiniLM-L6-v2`, then runs `src/04_setup_vector_db.py` to **build the Chroma index inside the image** from `data/processed/`. |
| `runtime` | `python:3.12-slim` | Copies only the venv, the model cache, the finished index, and the code (`src/`, `app/`, `tests/`). Runs as non-root `appuser` (UID 1000), offline for the embedding model (`HF_HUB_OFFLINE=1`), with a `HEALTHCHECK` on Streamlit's `/_stcore/health`. |

Why multi-stage: the builder needs build-time work (pip, model download, indexing) that the runtime
doesn't. Leaving that behind keeps the final image smaller, and the container starts ready —
no re-indexing and no embedding-model download on first request. `requirements-app.txt` is a
runtime-only subset of `requirements.txt` (no BeautifulSoup, python-docx, or LlamaIndex).

```bash
docker build -t pathfinder .
docker run --rm -p 7860:7860 -e GEMINI_API_KEY=<your-key> pathfinder    # http://localhost:7860
docker run --rm pathfinder python tests/smoke_test.py                   # offline tests, no key
docker run --rm pathfinder python tests/measure_retrieval_latency.py    # success-criterion check
docker images pathfinder                                                # note the size for the report
```

## 2. Environment variables and secrets handling

| Variable | Secret? | Default | Purpose |
|---|---|---|---|
| `GEMINI_API_KEY` | **Yes** | none (app shows a config error without it) | Gemini API access |
| `PORT` | No | `7860` | Port Streamlit listens on |
| `MAX_TURNS_PER_SESSION` | No | `30` | Per-conversation question cap (quota protection) |
| `MAX_QUESTION_CHARS` | No | `500` | Max question length |
| `HF_HUB_OFFLINE`, `ANONYMIZED_TELEMETRY` | No | `1`, `False` | No outbound calls from the embedder / Chroma at runtime |

Rules the project follows:

1. **The key is never in the image or the repo.** `.env` is in both `.gitignore` and `.dockerignore`;
   only `.env.example` (placeholder) is committed. The git history was scanned for Gemini-style keys
   (`AIza…`) and none were found.
2. **Injected at run time only:** `-e GEMINI_API_KEY=…` / `--env-file .env` locally, and a *Space
   secret* on Hugging Face (Settings → Variables and secrets). Space secrets are not visible in the
   public repo or build logs.
3. **CI never needs the key.** The smoke tests are retrieval-only and the health check uses a dummy
   value. The only CI secret is `HF_TOKEN` (deploy), stored in GitHub Actions secrets.
4. **Least privilege:** non-root user, no extra ports, no telemetry.
5. **Quota protection for a public URL:** per-session turn cap and question length cap; set a
   spending/quota limit and restrict the key in Google AI Studio. **If a key is ever leaked, revoke
   and re-create it** — deleting it from the latest commit is not enough.

## 3. Deploying to Hugging Face Spaces (free, public URL)

One-time setup:

1. huggingface.co → **New Space** → name `pathfinder-advisor` → SDK **Docker** (blank template) →
   hardware *CPU basic (free)* → visibility Public (or Private if the panel will be given access).
2. Space → **Settings → Variables and secrets → New secret**: `GEMINI_API_KEY` = your key.
3. huggingface.co → Settings → **Access Tokens** → new token with **Write** permission.
4. GitHub repo → **Settings → Secrets and variables → Actions**:
   * Secret `HF_TOKEN` = the token from step 3
   * Variable `HF_SPACE` = `<your-hf-username>/pathfinder-advisor`
5. Push to `main`. The workflow `.github/workflows/ci-cd.yml` builds the image, runs the tests, and
   (only if both pass) pushes the repo to the Space. Hugging Face then builds the same Dockerfile; the
   first build takes several minutes. Your public URL is
   `https://huggingface.co/spaces/<user>/pathfinder-advisor`.

*Manual alternative (no CI):* `git remote add space https://huggingface.co/spaces/<user>/pathfinder-advisor`,
add the Space front matter shown in the workflow to the top of `README.md`, and `git push space main`.

Notes: free Spaces go to sleep when idle — open the URL a few minutes before the defense. Any other
Docker host (Render, Railway, Fly.io, a VPS) also works: build the same image, set `GEMINI_API_KEY`
and `PORT` as environment variables.

## 4. Deployment evidence checklist (Deliverable 18)

Capture these for the report and the defense:

- [ ] Public/sandbox URL: `__________________________` (put it in README + Final Report)
- [ ] Screenshot: the live app answering a grounded question with the "Sources & retrieval details" panel open
- [ ] Screenshot: the out-of-scope refusal ("write me a haiku")
- [ ] Screenshot: a follow-up question resolved from memory ("How many units is it?")
- [ ] Screenshot: GitHub Actions run — green `build-test` and `deploy` jobs
- [ ] Screenshot: Space **Logs** / **Settings** showing the container is running and `GEMINI_API_KEY` listed as a secret (value hidden)
- [ ] Terminal output of `docker build`, `docker run … tests/smoke_test.py`, and `docker images pathfinder`
- [ ] Terminal output of `tests/measure_retrieval_latency.py` (fills in the Performance criterion)
- [ ] 1–2 min screen recording of the deployed app (also your backup if Wi-Fi fails during the defense)

## 5. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| App shows "Configuration problem: GEMINI_API_KEY not set" | Secret missing or misspelled in the Space / `docker run` |
| "couldn't reach the language model" | Free-tier Gemini quota hit (the repo already hit a 20 req/day limit once on a flagship model — see git history) or network error; wait and retry, or switch `MODEL_NAME` in `src/08_rag_app.py` |
| Docker build fails at `pip install torch` | Network blocked to `download.pytorch.org`; retry on a different network |
| Deploy job says "skipping deploy" | `HF_TOKEN` secret / `HF_SPACE` variable not set in GitHub |
| Space stuck on "Building" | Open the Space's **Logs** tab; first build downloads torch + the model |
