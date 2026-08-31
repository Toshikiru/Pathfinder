"""
Stage 0 - Curriculum Data (Real) + Course Descriptions & Policy Data (Simulated)
Writes the BSIS curriculum checklist (REAL, transcribed from an official,
signed TPC document) plus the course-description catalog and academic
policy documents that TPC does not publish anywhere (SIMULATED).

Curriculum: transcribed from a printed copy of Talibon Polytechnic College's
official BSIS curriculum checklist, effective A.Y. 2024-2025, based on CHED
Memorandum Order No. 25, s. 2015 and CMO No. 20, s. 2013. Prepared by
Flordelis A. Turtoga, MAMT (Program Head, BSIS); recommending approval by
the VP for Academic Affairs and VP for Administration; approved by the
College President. TPC does not publish this checklist online, but a
physical copy was obtained directly - see docs/Data_Sources.md for full
provenance. Every course code, title, unit/lecture/lab load, and
prerequisite below is real, not invented.

Course descriptions and policy wording remain SIMULATED: the official
checklist has no course-description catalog or student-handbook text, so
short descriptions (mapped to the real course codes above) and policy
wording are authored for this project, clearly labeled [SIMULATED DATA].

Output: data/raw/curriculum/*.txt, data/raw/policies/*.txt
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_DIR = ROOT / "data" / "raw" / "curriculum"
POLICIES_DIR = ROOT / "data" / "raw" / "policies"

REAL_DISCLOSURE = (
    "[REAL DATA] This is Talibon Polytechnic College's official BSIS "
    "curriculum checklist, effective A.Y. 2024-2025, based on CHED "
    "Memorandum Order No. 25, s. 2015 and CMO No. 20, s. 2013. Transcribed "
    "from a printed copy of the signed checklist (prepared by Flordelis A. "
    "Turtoga, MAMT, Program Head, BSIS; approved by the VP for Academic "
    "Affairs, VP for Administration, and College President). Every course "
    "code, title, unit/lecture/lab load, and prerequisite here is real, not "
    "invented - see docs/Data_Sources.md for full provenance.\n"
)

SIM_DISCLOSURE = (
    "[SIMULATED DATA] The official TPC BSIS curriculum checklist (see "
    "curriculum/*.txt) has no accompanying course-description catalog or "
    "student handbook, so this content is authored for this project. Course "
    "codes and titles referenced here are real (from the official "
    "checklist); the descriptive/policy wording itself is not an official "
    "TPC document. See docs/Data_Sources.md for full provenance.\n"
)

# code, title, units, lecture hrs, lab hrs, prerequisite (raw text as printed
# on the checklist: a course code, "CO-<code>" for corequisite, a standing
# requirement, "A & B" for multiple, or "-" for none)
Course = tuple

TERMS: dict[str, list[Course]] = {
    "Year 1 - First Semester": [
        ("CC 100", "Introduction to Computing", 3, 2, 3, "-"),
        ("CC 101", "Computer Programming 1", 3, 2, 3, "-"),
        ("GECC 101", "Purposive Communication", 3, 3, 0, "-"),
        ("GECC 102", "Understanding the Self", 3, 3, 0, "-"),
        ("GECC 103", "Mathematics in the Modern World", 3, 3, 0, "-"),
        ("GELEC 101", "Living in the IT Era", 3, 3, 0, "-"),
        ("GECC 104", "The Contemporary World", 3, 3, 0, "-"),
        ("GELEC 102", "The Entrepreneurial Mind", 3, 3, 0, "-"),
        ("PATHFIT 1", "Physical Fitness and Health", 2, 2, 0, "-"),
        ("NSTP 1", "LTS/CWTS 1", 3, 3, 0, "-"),
    ],
    "Year 1 - Second Semester": [
        ("IS 101", "Fundamentals of Information Systems", 3, 3, 0, "CC 101"),
        ("CC 102", "Computer Programming 2", 3, 2, 3, "CC 100"),
        ("HCI 1", "Human Computer Interaction", 3, 2, 3, "GECC 104"),
        ("GECC 105", "Art Appreciation", 3, 3, 0, "-"),
        ("GEELEC 103", "Philippine Popular Culture", 3, 3, 0, "-"),
        ("GECC 106", "Science, Technology & Society", 3, 3, 0, "-"),
        ("PATHFIT 2", "Dance & Rhythmic Activities", 2, 2, 0, "PATHFIT 1"),
        ("NSTP 2", "LTS/CWTS 2", 3, 3, 0, "NSTP 1"),
    ],
    "Year 2 - First Semester": [
        ("CC 103", "Data Structures and Algorithms", 3, 2, 3, "CC 102"),
        ("IS 102", "Professional Issues in Information", 3, 3, 0, "2nd Year Standing"),
        ("IS 103", "IT Infrastructures and Network", 3, 2, 3, "IS 101"),
        ("BED 101", "Organization and Management Concepts", 3, 3, 0, "2nd Year Standing"),
        ("BED 102", "Financial Management", 3, 3, 0, "CO-BED 101"),
        ("DM 101", "Discrete Mathematics", 3, 3, 0, "-"),
        ("GECC 107", "Ethics", 3, 3, 0, "-"),
        ("PATHFIT 3", "Individual and Dual Sports", 2, 2, 0, "PATHFIT 2"),
    ],
    "Year 2 - Second Semester": [
        ("CC 104", "Information Management", 3, 2, 3, "CC 103"),
        ("IS 104", "System Analysis & Design", 3, 3, 0, "IS 103"),
        ("IPT 101", "Integrative Programming and Technologies", 3, 2, 3, "HCI 1"),
        ("BED 103", "Business Process Management", 3, 3, 0, "BED 102"),
        ("BED 104", "Evaluation of Business Performance", 3, 3, 0, "CO-BED 103"),
        ("ISEL #1", "IS Professional Elective #1", 3, 3, 0, "2nd Year Standing"),
        ("GECC 108", "Readings in the Philippine History", 3, 3, 0, "-"),
        ("PATHFIT 4", "Team Sports", 2, 2, 0, "PATHFIT 3"),
    ],
    "Year 3 - First Semester": [
        ("RIZAL", "Life and Works of Rizal", 3, 3, 0, "IS 104"),
        ("IS 105", "Enterprise Architecture", 3, 2, 3, "3rd Year Standing"),
        ("IS 108", "IT Security and Management", 3, 3, 0, "-"),
        ("ISEL #2", "IS Professional Elective #2", 3, 3, 0, "ISEL #1"),
        ("DM 102", "Quantitative Methods", 3, 3, 0, "DM 101"),
        ("RESEARCH", "Methods of Research", 3, 3, 0, "3rd Year Standing"),
        ("CC 105", "Application Development and Emerging Technologies", 3, 2, 3, "IPT 101 & CC 104"),
    ],
    "Year 3 - Second Semester": [
        ("CAP 101", "Capstone Project I", 3, 3, 0, "3rd Year Standing"),
        ("IS 106", "IS Project Management", 3, 3, 0, "DM 102"),
        ("IS 107", "Software Engineering", 3, 3, 0, "IS 106"),
        ("ISEL #3", "IS Professional Elective #3", 3, 3, 0, "ISEL #2"),
    ],
    "Year 4 - First Semester": [
        ("CAP 102", "Capstone Project II", 3, 3, 0, "CAP 101"),
        ("IS 109", "IS Strategy, Management and Acquisition", 3, 3, 0, "IS 106"),
        ("ISEL #4", "IS Professional Elective #4", 3, 3, 0, "ISEL #3"),
        ("SFT 101", "Seminar/Educational Tour/Field Trip", 1, 0, 0, "4th Year Standing"),
    ],
    "Year 4 - Second Semester": [
        ("PRACTICUM", "Practicum for Information Systems (486 Hours)", 6, 0, 0, "4th Year Standing"),
    ],
}


def format_prereq_note(code: str, title: str, prereq: str, course_index: dict[str, str]) -> str | None:
    if prereq == "-":
        return None
    if prereq.startswith("CO-"):
        ref = prereq[3:].strip()
        name = course_index.get(ref, "")
        return f"- {code} {title}: co-requisite with {ref}{f' ({name})' if name else ''}."
    if "Standing" in prereq:
        return f"- {code} {title}: requires {prereq}."
    if "&" in prereq:
        parts = [p.strip() for p in prereq.split("&")]
        named = [f"{p} ({course_index.get(p, 'see curriculum')})" for p in parts]
        return f"- {code} {title}: requires {' and '.join(named)}."
    name = course_index.get(prereq, "")
    return f"- {code} {title}: requires {prereq}{f' ({name})' if name else ''}."


def write_curriculum_files() -> None:
    CURRICULUM_DIR.mkdir(parents=True, exist_ok=True)
    course_index: dict[str, str] = {}
    for courses in TERMS.values():
        for code, title, *_ in courses:
            course_index[code] = title

    for i, (term, courses) in enumerate(TERMS.items(), start=1):
        lines = [REAL_DISCLOSURE, ""]
        lines.append(f"BSIS Curriculum Checklist - {term}")
        lines.append("Program: Bachelor of Science in Information Systems (BSIS)")
        lines.append("Talibon Polytechnic College")
        lines.append("")
        lines.append(f"{'Code':<10}{'Course Title':<55}{'Units':<7}{'Lec':<5}{'Lab':<5}Prerequisite(s)")
        total_units = total_lec = total_lab = 0
        for code, title, units, lec, lab, prereq in courses:
            total_units += units
            total_lec += lec
            total_lab += lab
            prereq_str = "None" if prereq == "-" else prereq
            lines.append(f"{code:<10}{title:<55}{units:<7}{lec:<5}{lab:<5}{prereq_str}")
        lines.append("")
        lines.append(f"Total units this term: {total_units} (Lecture: {total_lec}, Lab: {total_lab})")
        lines.append("")
        lines.append("Prerequisite notes:")
        notes = [format_prereq_note(code, title, prereq, course_index) for code, title, _, _, _, prereq in courses]
        notes = [n for n in notes if n]
        if notes:
            lines.extend(notes)
        else:
            lines.append("- No prerequisite courses this term.")

        fname = f"{i:02d}_" + term.lower().replace(" - ", "_").replace(" ", "_") + ".txt"
        (CURRICULUM_DIR / fname).write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote {fname}")


# Course descriptions: authored (simulated) content mapped to the REAL
# course codes/titles above. The official checklist has no description
# catalog, so this fills that gap the same way the old simulated set did -
# only the codes/titles underneath are now real instead of invented.
DESCRIPTION_GROUPS = {
    "course_descriptions_programming_and_systems.txt": [
        ("CC 100", "Introduction to Computing",
         "Foundational course covering computer hardware/software basics, number systems, and problem-solving concepts before formal programming begins."),
        ("CC 101", "Computer Programming 1",
         "Introduces programming fundamentals: variables, control structures, functions, and basic data types through small console programs."),
        ("CC 102", "Computer Programming 2",
         "Builds on CC 101 with object-oriented programming: classes, objects, inheritance, and polymorphism."),
        ("CC 103", "Data Structures and Algorithms",
         "Covers arrays, linked lists, stacks, queues, trees, and sorting/searching algorithms, with emphasis on choosing the right structure for a problem."),
        ("CC 104", "Information Management",
         "Covers relational database design, normalization, SQL, and data modeling for information systems."),
        ("CC 105", "Application Development and Emerging Technologies",
         "Hands-on application-building course integrating current tools/platforms (e.g. APIs, cloud, or mobile) into a working multi-module system."),
        ("IPT 101", "Integrative Programming and Technologies",
         "Covers integrating multiple programming languages/technologies (e.g. a web front end, backend services, and APIs) into one cohesive application."),
        ("HCI 1", "Human Computer Interaction",
         "Covers usability principles, interface design, and evaluating software from the end user's perspective."),
        ("IS 104", "System Analysis & Design",
         "Teaches requirements gathering, process modeling (DFDs, use cases), and translating business needs into system specifications."),
        ("IS 107", "Software Engineering",
         "Covers the software development lifecycle, methodologies (e.g. Agile/Scrum), and software quality/testing practices."),
    ],
    "course_descriptions_data_networks_security.txt": [
        ("IS 103", "IT Infrastructures and Network",
         "Introduces networking fundamentals and IT infrastructure: OSI/TCP-IP models, IP addressing, servers, and basic network configuration."),
        ("IS 105", "Enterprise Architecture",
         "Covers modeling an organization's IT systems, data, and processes as an integrated enterprise architecture aligned with business strategy."),
        ("IS 108", "IT Security and Management",
         "Covers information security fundamentals (confidentiality/integrity/availability, common threats) and managing security within an organization."),
    ],
    "course_descriptions_is_management_and_capstone.txt": [
        ("IS 101", "Fundamentals of Information Systems",
         "Foundational course distinguishing Information Systems from Computer Science/IT; covers the role of IS in organizations."),
        ("IS 102", "Professional Issues in Information",
         "Covers ethical, legal, and professional issues IS practitioners face, including data privacy and professional conduct."),
        ("IS 106", "IS Project Management",
         "Introduces project management fundamentals (scope, schedule, cost, risk) applied to IS/software projects."),
        ("IS 109", "IS Strategy, Management and Acquisition",
         "Covers IT governance, sourcing/acquisition decisions, and aligning IS strategy with overall business strategy."),
        ("BED 101", "Organization and Management Concepts",
         "Introduces organizational structures, management functions, and decision-making relevant to deploying IS in a business."),
        ("BED 102", "Financial Management",
         "Covers financial statement analysis, budgeting, and financial decision-making relevant to managing IS projects/departments."),
        ("BED 103", "Business Process Management",
         "Covers modeling, analyzing, and improving business processes, and how IS supports process automation."),
        ("BED 104", "Evaluation of Business Performance",
         "Covers performance metrics and evaluation frameworks for assessing how well an organization (and its IS investments) are performing."),
        ("DM 101", "Discrete Mathematics",
         "Covers logic, set theory, combinatorics, and graph theory foundational to computing and algorithm analysis."),
        ("DM 102", "Quantitative Methods",
         "Covers statistical and quantitative analysis techniques used for business and IS decision-making."),
        ("RESEARCH", "Methods of Research",
         "Introduces research methodology (research design, data collection, analysis) needed to complete the Capstone Project."),
        ("CAP 101", "Capstone Project I",
         "First half of the two-term capstone: students form a team, propose a real-world IS project, and complete requirements/design."),
        ("CAP 102", "Capstone Project II",
         "Second half of the capstone: students implement, test, and defend the system proposed in Capstone Project I."),
        ("PRACTICUM", "Practicum for Information Systems",
         "486-hour supervised work experience in an IS-related role at a partner company or organization."),
    ],
}


def write_description_files() -> None:
    CURRICULUM_DIR.mkdir(parents=True, exist_ok=True)
    for fname, entries in DESCRIPTION_GROUPS.items():
        lines = [SIM_DISCLOSURE, "", "BSIS Course Description Catalog (excerpt)", ""]
        for code, title, desc in entries:
            lines.append(f"{code} - {title}")
            lines.append(desc)
            lines.append("")
        (CURRICULUM_DIR / fname).write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote {fname}")


POLICY_DOCS = {
    "grading_system_and_gwa_policy.txt": """
BSIS Program - Grading System and GWA Policy

Numeric grades range from 1.00 (highest) to 5.00 (failing), following the
standard Philippine collegiate scale used across TPC programs:

1.00 = 97-100%    2.00 = 83-86%     3.00 = 75-77%
1.25 = 94-96%     2.25 = 80-82%     5.00 = Below 75% (Failed)
1.50 = 91-93%     2.50 = 77-79%     INC  = Incomplete
1.75 = 88-90%     2.75 = 75-77%     DRP  = Dropped

A student's General Weighted Average (GWA) is the unit-weighted mean of all
numeric grades for the term: sum(grade x units) / sum(units). Latin honors
eligibility (Cum Laude and above) requires a cumulative GWA of 1.75 or
better with no grade lower than 2.5 in any course, and no record of a
failing (5.00) grade in any course throughout the program.

A student who receives INC must complete the missing requirement within
one (1) year, or the grade automatically converts to 5.00 (Failed).
""",
    "enrollment_prerequisites_and_academic_standing.txt": """
BSIS Program - Enrollment, Prerequisites, and Academic Standing Policy

Prerequisite enforcement: a student may not enroll in a course until every
prerequisite listed for it in the curriculum checklist has been passed
(grade of 3.00 or better). Registration will be blocked for any course
whose prerequisite is missing, failed, or currently "in progress" in the
same term.

Course load: a regular BSIS student may enroll in a maximum of 24 units per
regular semester (Year 1-4 Sem 1/Sem 2) and 9 units in the summer term. A
student on academic probation is capped at 15 units per regular semester
until good standing is restored.

Academic standing:
- Good Standing: term GWA of 3.00 or better with no more than one failing
  grade in the current term.
- Probation: a student who fails 2 or more courses in a single term, or
  whose cumulative GWA falls below 3.00, is placed on academic probation
  for the following term.
- Dismissal: a student placed on probation for two consecutive terms, or
  who fails the same required course three times, is subject to academic
  dismissal from the BSIS program, pending an appeal to the Program Head.

Capstone eligibility: enrollment in CAP 101 (Capstone Project I) requires
3rd Year Standing, per the curriculum checklist. Enrollment in CAP 102
(Capstone Project II) requires completion of CAP 101. Enrollment in
PRACTICUM (Practicum for Information Systems, 486 hours) requires 4th Year
Standing.

Add/drop: students may add or drop a course only within the first two (2)
weeks of a regular semester (first week for the summer term), subject to
the Registrar's published academic calendar.
""",
}


def write_policy_files() -> None:
    POLICIES_DIR.mkdir(parents=True, exist_ok=True)
    for fname, body in POLICY_DOCS.items():
        content = SIM_DISCLOSURE + "\n" + body.strip() + "\n"
        (POLICIES_DIR / fname).write_text(content, encoding="utf-8")
        print(f"wrote {fname}")


if __name__ == "__main__":
    write_curriculum_files()
    write_description_files()
    write_policy_files()
