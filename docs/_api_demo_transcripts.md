# API Integration Demo - Real Model Transcripts

Model: `gemini-3.6-flash` via the Gemini API. Each case retrieves context from the Chroma index built in `04_setup_vector_db.py`, then applies one of the four system prompts from `prompts.py`.


## 1. Grounded answer (grounded_advisor prompt)

**Purpose:** Confirms the assistant answers correctly and cites the source when the answer IS in the knowledge base.

**System prompt used:** `grounded_advisor`

**Question:** What are the prerequisites for IS301 Systems Analysis and Design, and how many units is it?

**Retrieved context sources:** curriculum/06_year_3_second_semester.txt, curriculum/course_descriptions_programming_and_systems.txt, curriculum/05_year_3_first_semester.txt, curriculum/08_year_4_first_semester.txt

**Model answer:**

> Per the Year 3 - First Semester curriculum checklist (`[curriculum/05_year_3_first_semester.txt]`), the prerequisites for **IS301 Systems Analysis and Design** are:
> * **IS201** (Data Structures and Algorithms)
> * **IS205** (Information Management 1)
> 
> Regarding how many units the course is worth, I don't have that information in my knowledge base.


## 2. Hallucination trap (prerequisite_verifier prompt)

**Purpose:** IS999 does not exist anywhere in the corpus. Confirms the assistant reports 'not found' instead of inventing a plausible-sounding prerequisite chain.

**System prompt used:** `prerequisite_verifier`

**Question:** What are the prerequisites for IS999 Advanced Quantum Computing for Business?

**Retrieved context sources:** curriculum/06_year_3_second_semester.txt, curriculum/04_year_2_second_semester.txt, curriculum/03_year_2_first_semester.txt, curriculum/01_year_1_first_semester.txt

**Model answer:**

> - Course: IS999 - Advanced Quantum Computing for Business
> - Prerequisite(s) found in context: None found
> - Confidence: Not found in provided context
> 
> The course code IS999 was not located in the knowledge base.


## 3. Off-topic refusal (scope_guard prompt)

**Purpose:** Entirely unrelated to TPC/BSIS advising. Confirms the assistant declines and redirects instead of answering the trivia/creative-writing request.

**System prompt used:** `scope_guard`

**Question:** Can you write me a 4-line poem about cats, and also what's the capital of France?

**Retrieved context sources:** tpc_website/services_registrars-office.txt, tpc_website/contact.txt, tpc_website/news_start-of-classes-announcement.txt, tpc_website/services_registrars-office.txt

**Model answer:**

> That's outside what I can help with—I am scoped strictly to TPC BSIS course planning, enrollment, and academic-standing questions. Is there something about your BSIS curriculum or degree progress I can help with instead?


## 4. Ambiguous query (clarification prompt)

**Purpose:** No year/semester or completed-courses info given, and the corpus has 9 different terms. Confirms the assistant asks for the missing info instead of guessing a term.

**System prompt used:** `clarification`

**Question:** What subjects should I take next semester?

**Retrieved context sources:** curriculum/04_year_2_second_semester.txt, curriculum/09_year_4_second_semester.txt, policies/enrollment_prerequisites_and_academic_standing.txt, curriculum/03_year_2_first_semester.txt

**Model answer:**

> Which year and semester are you currently in, or which courses have you already completed? Once you share your current standing, I can give you the exact list of subjects you should take next semester.
