# Pathfinder — CP1 & CP2 Presentation Script (Simple Version)

This is your script. **RUN** = type this in the terminal. **SAY** = say
this out loud, in your own words. Simple as that.

Before you present: make sure your venv is on, packages are installed, and
your `.env` file has your real API key in it. Don't show that file on
screen — it's your secret key.

---

## One-time setup: put this project on GitHub

Do this once, before you present. Your instructor wants to see your code
in a real GitHub repo, with your commit history showing steady progress —
not one big upload at the end.

**1. Make a new repo on GitHub**
- Go to [github.com](https://github.com) and log in (make an account if you
  don't have one).
- Click the **+** icon top-right → **New repository**.
- Name it something like `pathfinder-academic-advisor`.
- Leave it **empty** — don't check "Add a README" or "Add .gitignore." Your
  project already has those, and checking those boxes causes a conflict.
- Click **Create repository**.
- On the next page, copy the URL that looks like
  `https://github.com/your-username/pathfinder-academic-advisor.git`.

**2. Connect your local project to it**

Open your terminal in the project folder and run these one at a time:

```bash
git remote add origin https://github.com/your-username/pathfinder-academic-advisor.git
```
*(paste the URL you copied — this just tells your project "this is where
GitHub lives")*

```bash
git push -u origin main
```
*(this uploads everything — all your commits, all your files)*

It may ask you to log in — follow the prompts (GitHub will likely open a
browser window to confirm it's you).

**3. Check it worked**

Refresh the GitHub page in your browser. You should see all your files —
`src/`, `docs/`, `README.md`, everything — and your commit history under
the "commits" link.

**One important thing:** your `.env` file with your real API key should
**not** show up on GitHub. It's already listed in `.gitignore` so Git skips
it automatically — just double check it's not there after pushing.

**From now on**, every time you finish new work, save it to GitHub with:

```bash
git add .
git commit -m "describe what you changed here"
git push
```

---

## Start with this

**SAY:**
> "Pathfinder is a chatbot that answers school questions for BSIS students —
> things like 'what subjects do I need to take next' or 'what's the
> passing grade.' Instead of guessing, it looks up real documents first,
> then answers based on what it finds. That's called RAG — Retrieval
> Augmented Generation. Basically: look it up, then answer."

---

## Part 1: Checkpoint 1 — Getting the Data Ready

**SAY:**
> "Before a chatbot can answer questions, it needs data to read. Checkpoint
> 1 is all about collecting that data and cleaning it up."

**SHOW:** `docs/Project_Proposal.docx`

**SAY:**
> "This is our proposal. It says what problem we're solving, who it's for,
> where our data comes from, and how we'll know if it worked."

**SHOW:** `docs/Data_Sources.md`

**SAY:**
> "We have 23 documents. 10 are real, copied straight from TPC's website —
> just the BSIS program page and general campus info now, we dropped the
> pages about other TPC degree programs since they didn't belong in a BSIS
> advisor's knowledge base. Another 8 are also real — the official BSIS
> curriculum checklist, the actual subject list with real course codes and
> prerequisites, which isn't published online, so we got a printed, signed
> copy directly and transcribed it. The remaining 5 — short course
> descriptions and the grading/policy rules — genuinely aren't available
> anywhere accessible (there's a school handbook we couldn't get past a
> locked preview of), so we built those ourselves and clearly labeled every
> one of them `[SIMULATED DATA]`, so nobody gets confused about what's
> real."

Now run the data pipeline, one step at a time:

**RUN:**
```bash
python3 src/00_generate_curriculum_data.py
```
**SAY:** "This creates our simulated subject list and school policies."

**RUN:**
```bash
python3 src/01_extract_raw_text.py
```
**SAY:**
> "This pulls the plain text out of the web pages we saved. Websites are
> full of extra code and buttons — this step just grabs the actual words."

**RUN:**
```bash
python3 src/02_preprocess.py
```
**SAY (while the before/after text shows up):**
> "Real website text is messy — menus, footers, broken email addresses. This
> step cleans all of that out so only the useful text is left. Look — before
> and after, right there on screen."

**RUN:**
```bash
python3 src/03_generate_embeddings.py
```
**SAY:**
> "Now here's the important part. Computers don't understand words the way
> we do — they understand numbers. So we turn every piece of text into a
> list of numbers called an 'embedding.' Sentences that mean similar things
> end up with similar numbers. That's how the computer will later find the
> right answer — by matching numbers, not just matching words."

**SHOW:** `docs/Reflection_Checkpoint1.md` — read the last part out loud.

**SAY:**
> "While testing this, we noticed something: sometimes the bot picked the
> wrong piece of text because we were searching whole documents instead of
> smaller pieces. Good thing to catch early — that's exactly what
> Checkpoint 2 starts to fix."

---

## Part 2: Checkpoint 2 — Teaching the Bot to Answer Safely

**SAY:**
> "Checkpoint 2 has two jobs: build a smart search system for our data, and
> teach the bot rules so it doesn't make things up."

**RUN:**
```bash
python3 src/04_setup_vector_db.py
```
**SAY:**
> "This loads all our text into something called a vector database — think
> of it like a super-organized filing cabinet. When you ask a question, it
> instantly finds the pieces of text closest in meaning to your question.
> Look — ask about academic probation, and it finds the exact rule about
> the 15-unit limit. That's the filing cabinet working."

**RUN:**
```bash
python3 src/05_distance_metric_comparison.py
```
**SHOW:** `docs/Distance_Metric_Comparison.md`

**SAY:**
> "There's more than one way to measure 'closeness' between two pieces of
> text. We tried three different ways and compared them on our own data. All
> three gave the exact same results, and we explain why in the report. We're
> using the method called 'cosine similarity' going forward."

**SHOW:** `docs/Prompt_Engineering.md`

**SAY:**
> "Now, the important safety part. AI chatbots sometimes make up answers
> that sound believable but are completely false — that's called
> 'hallucinating.' To stop that, we wrote 4 clear rule sets for the bot:
> one for answering normal questions honestly, one for double-checking
> prerequisites, one for politely saying 'that's not something I can help
> with' when asked off-topic stuff, and one for asking a follow-up question
> instead of guessing when something's unclear. Every example in this
> document is a real answer the bot actually gave — nothing here is made up
> by us."

**RUN — the fun part, do this live:**
```bash
python3 src/06_api_integration_demo.py
```

**SAY while it runs 4 test questions automatically:**
> "Watch it answer 4 test questions: one it answers correctly with a
> source, one where it correctly says 'that course doesn't exist' instead
> of making something up, one where it politely refuses an off-topic
> question, and one where it asks us a clarifying question instead of
> guessing."

Then it will say `Your question:` and wait for you to type. Try these,
live, in front of everyone:

- `What are the prerequisites for CC 104 Information Management?`
  → it answers correctly and tells you where the answer came from
- `How many units can I enroll in while on academic probation?`
  → it gives the exact number, 15
- `What's the weather like today?`
  → it politely says "that's not something I can help with"
- `What subjects should I take next?`
  → it asks you what year and semester you're in first, instead of guessing
- `What are the prerequisites for IS777 Blockchain for Farmers?`
  → a course that doesn't exist — watch it say so instead of inventing an answer

Type `quit` when you're done.

**If the internet hiccups or the API gives an error:**
**SAY:**
> "No worries — this is actually our error handling doing its job. Instead
> of crashing, it tells us clearly what went wrong."

Then just try again, or show the saved answers in `docs/_api_demo_transcripts.md`.

---

## Wrap it up

**SAY:**
> "So, quick recap: Checkpoint 1 got us clean, honest data. Checkpoint 2
> taught the bot to search that data smartly and answer safely without
> making things up. Next, Checkpoint 3 turns this into a full chat app that
> remembers the conversation."

---

## If something goes wrong

- **Search results look empty or old** → run `python3 src/04_setup_vector_db.py` again.
- **Says the API key is missing** → check your `.env` file has your real key, not the placeholder.
- **Says "quota exceeded" / too many requests** → we already switched to a
  model with a bigger free daily limit for this reason. If it still
  happens, just wait a bit or use the saved answers instead.
- **An answer looks weak or incomplete** → be honest about it: "that's a
  known limitation we already wrote down, and we're improving it in the
  next checkpoint." That's a much better answer than pretending everything
  is perfect.
