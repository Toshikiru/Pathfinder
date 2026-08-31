# RAG Application Demo Transcripts (Checkpoint 3)

Model: `gemini-3.5-flash-lite` via `langchain-google-genai`, retrieval via `langchain-chroma` over the existing Chroma index. Each turn shows the standalone (memory-resolved) search query actually used for retrieval, so it's visible when conversational memory changed what was searched for.


## Turn 1

**Question:** What are the prerequisites for IS 104 System Analysis & Design?

**Retrieved sources:** curriculum/04_year_2_second_semester.txt, curriculum/05_year_3_first_semester.txt, curriculum/04_year_2_second_semester.txt, curriculum/06_year_3_second_semester.txt

**Answer:**

> Based on `curriculum/04_year_2_second_semester.txt`, the prerequisite for IS 104 System Analysis & Design is IS 103 (IT Infrastructures and Network).


## Turn 2

**Question:** How many units is it?

**Standalone search query (memory-resolved):** How many units is IS 104 System Analysis & Design?

**Retrieved sources:** curriculum/course_descriptions_data_networks_security.txt, curriculum/04_year_2_second_semester.txt, curriculum/06_year_3_second_semester.txt, curriculum/05_year_3_first_semester.txt

**Answer:**

> I don't have that information in my knowledge base.


## Turn 3

**Question:** What's the GWA requirement for Latin honors?

**Standalone search query (memory-resolved):** What is the Grade Weighted Average (GWA) requirement for graduating with Latin honors?

**Retrieved sources:** policies/grading_system_and_gwa_policy.txt, policies/grading_system_and_gwa_policy.txt, policies/enrollment_prerequisites_and_academic_standing.txt, tpc_website/admission.txt

**Answer:**

> Based on `policies/grading_system_and_gwa_policy.txt`, graduating with Latin honors (Cum Laude and above) requires a cumulative GWA of 1.75 or better, with no grade lower than 2.5 in any course, and no record of a failing (5.00) grade in any course throughout the program.


## Turn 4

**Question:** Can you write me a haiku about databases instead?

**Standalone search query (memory-resolved):** Write a haiku about databases.

**Retrieved sources:** curriculum/03_year_2_first_semester.txt, curriculum/course_descriptions_programming_and_systems.txt, curriculum/04_year_2_second_semester.txt, tpc_website/services_registrars-office.txt

**Answer:**

> I can only assist with TPC/BSIS academic advising topics.


## Turn 5

**Question:** What about CC 105 - what does that one require?

**Standalone search query (memory-resolved):** What are the prerequisites for CC 105?

**Retrieved sources:** curriculum/02_year_1_second_semester.txt, curriculum/05_year_3_first_semester.txt, curriculum/course_descriptions_programming_and_systems.txt, curriculum/course_descriptions_programming_and_systems.txt

**Answer:**

> Based on `curriculum/05_year_3_first_semester.txt`, the prerequisites for CC 105 Application Development and Emerging Technologies are IPT 101 (Integrative Programming and Technologies) and CC 104 (Information Management).


## Turn 6

**Question:** How many units can I enroll in if I'm on academic probation?

**Standalone search query (memory-resolved):** What is the maximum number of units a student on academic probation is allowed to enroll in?

**Retrieved sources:** policies/enrollment_prerequisites_and_academic_standing.txt, policies/enrollment_prerequisites_and_academic_standing.txt, policies/enrollment_prerequisites_and_academic_standing.txt, policies/enrollment_prerequisites_and_academic_standing.txt

**Answer:**

> Based on `policies/enrollment_prerequisites_and_academic_standing.txt`, a student on academic probation is capped at a maximum of 15 units per regular semester.


## Turn 7

**Question:** How many subjects are there in first year first sem?

**Standalone search query (memory-resolved):** What are the courses or subjects included in the first year, first semester curriculum?

**Year/semester filter applied:** Year 1, Semester 1

**Retrieved sources:** curriculum/01_year_1_first_semester.txt, curriculum/01_year_1_first_semester.txt, curriculum/01_year_1_first_semester.txt

**Answer:**

> Based on `curriculum/01_year_1_first_semester.txt`, the courses included in the first year, first semester curriculum are:
> 
> - CC 100: Introduction to Computing (3 units)
> - CC 101: Computer Programming 1 (3 units)
> - GECC 101: Purposive Communication (3 units)
> - GECC 102: Understanding the Self (3 units)
> - GECC 103: Mathematics in the Modern World (3 units)
> - GELEC 101: Living in the IT Era (3 units)
> - GECC 104: The Contemporary World (3 units)
> - GELEC 102: The Entrepreneurial Mind (3 units)
> - PATHFIT 1: Physical Fitness and Health (2 units)
> - NSTP 1: LTS/CWTS 1 (3 units)


## Turn 8

**Question:** What about second sem?

**Standalone search query (memory-resolved):** What subjects are included in the first year, second semester curriculum?

**Year/semester filter applied:** Year 1, Semester 2

**Retrieved sources:** curriculum/02_year_1_second_semester.txt, curriculum/02_year_1_second_semester.txt, curriculum/02_year_1_second_semester.txt, curriculum/02_year_1_second_semester.txt

**Answer:**

> Based on `curriculum/02_year_1_second_semester.txt`, the subjects included in the first year, second semester curriculum are:
> 
> - IS 101: Fundamentals of Information Systems (3 units)
> - CC 102: Computer Programming 2 (3 units)
> - HCI 1: Human Computer Interaction (3 units)
> - GECC 105: Art Appreciation (3 units)
> - GEELEC 103: Philippine Popular Culture (3 units)
> - GECC 106: Science, Technology & Society (3 units)
> - PATHFIT 2: Dance & Rhythmic Activities (2 units)
> - NSTP 2: LTS/CWTS 2 (3 units)
