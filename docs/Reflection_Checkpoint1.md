# Checkpoint 1 Reflection — What Was Messy, and How It Was Handled

**What was messy about the real data.** The TPC website is built with a
JS-heavy component framework (Alpine.js/Tailwind). A first-pass extraction
using a naive regex tag-stripper (`re.sub(r"<[^>]+>", "", html)`) leaked raw
JavaScript expressions into the "text" — fragments like
`0 || document.activeElement === $refs.input` — because Alpine's inline
`x-data`/`x-bind` attributes contain literal `>` characters that broke the
regex's tag boundary. Switching to a real HTML parser (BeautifulSoup, dropping
`<script>`/`<style>` before calling `.get_text()`) fixed this — the lesson
being that "strip the tags" is not the same as "understand the markup," and a
regex scraper will silently produce corrupted text on any site with inline
JS in attributes rather than failing loudly. Even after that fix, every page
still carried ~35 lines of repeated site-chrome (nav links, a search widget's
placeholder copy, the footer, a feedback-form widget) that had nothing to do
with academic advising, plus a Cloudflare email-obfuscation artifact
(`[email protected]`) where the registrar's real email should be — the
scraper caught the un-rendered placeholder, not the JS-decoded address.
`02_preprocess.py` removes the repeated boilerplate via a known-lines set and
patches the email placeholder; together this cut total corpus size by
~28% (60,066 → 43,323 characters) without losing any advising-relevant content.

**What was missing, not just messy.** The deeper problem wasn't formatting —
it was that TPC's public website simply does not publish the one thing this
project's theme actually depends on: the curriculum checklist (course codes,
units, prerequisites) and academic policies (grading, probation, add/drop).
That data lives in a registrar prospectus and a 52-page student handbook that
aren't posted online (the handbook exists on Scribd but is preview-locked).
Rather than quietly inventing course requirements, this gap is filled with a
dataset built from CHED Memorandum Order No. 25, s. 2015 — the real national
policy that governs how Philippine BSIS programs are structured — and every
file generated from it is labeled `[SIMULATED DATA]` in its first line, with
full disclosure in `docs/Data_Sources.md`. This felt like the more honest
choice than picking an easier theme with no real gaps to navigate, and it
mirrors a realistic situation for a production system: sometimes the
authoritative source isn't publicly scrapable, and you have to be explicit
about which parts of your knowledge base are verified fact versus a
best-effort reconstruction.

**One more thing the embedding demo surfaced.** In `03_generate_embeddings.py`,
the query *"What courses cover database design?"* matched a curriculum
checklist chunk (similarity 0.444) instead of the course-description chunk
that actually explains IS205 covers "relational database design,
normalization, SQL" — because at whole-document chunking granularity, a
7-course table competes evenly with a one-paragraph description. That's a
preview of a Checkpoint 2/3 concern (chunk size and boundaries matter a lot
for retrieval quality), not something to fix yet — but it was worth writing
down while fresh instead of rediscovering it later.
