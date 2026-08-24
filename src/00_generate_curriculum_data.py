"""
Stage 0 - Simulated Data Generation
Generates the BSIS curriculum checklist, course-description catalog, and
academic policy documents that TPC does not publish on its public website.

These are SIMULATED but realistically grounded: the term-by-term structure,
course sequencing, and unit loads are adapted from CHED Memorandum Order
No. 25, s. 2015 ("Policies, Standards and Guidelines for BS Computer Science,
BS Information Systems, and BS Information Technology Programs"), which is
the actual national policy Philippine HEIs use to build BSIS curricula.
Course codes, exact descriptions, and campus-specific policy wording are
authored for this project, not copied from a real TPC document, since TPC's
internal prospectus/handbook is not publicly accessible.

Output: data/raw/curriculum/*.txt, data/raw/policies/*.txt
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_DIR = ROOT / "data" / "raw" / "curriculum"
POLICIES_DIR = ROOT / "data" / "raw" / "policies"

DISCLOSURE = (
    "[SIMULATED DATA] This document is a realistic reconstruction for the "
    "Pathfinder capstone project. It is modeled on CHED Memorandum Order "
    "No. 25, s. 2015 (BSIS program standards) and adapted for Talibon "
    "Polytechnic College's BSIS program. It is NOT an official TPC "
    "document; TPC's actual registrar prospectus is not publicly available "
    "online. Course codes and exact wording are authored for this project.\n"
)

# course code, title, units, prereq codes (list), notes
Course = tuple

TERMS: dict[str, list[Course]] = {
    "Year 1 - First Semester": [
        ("IS101", "Introduction to Computing", 3, [], "No prior programming background assumed."),
        ("IS102", "Computer Programming 1 (Fundamentals of Programming)", 3, [], "Introduces variables, control structures, and functions."),
        ("GE101", "Mathematics in the Modern World", 3, [], ""),
        ("GE102", "Understanding the Self", 3, [], ""),
        ("GE103", "Komunikasyon sa Akademikong Filipino", 3, [], ""),
        ("PE101", "Physical Fitness", 2, [], ""),
        ("NSTP101", "National Service Training Program 1", 3, [], ""),
    ],
    "Year 1 - Second Semester": [
        ("IS103", "Fundamentals of Information Systems", 3, ["IS101"], "Introduces the IS discipline and how it differs from CS/IT."),
        ("IS104", "Computer Programming 2 (Intermediate Programming)", 3, ["IS102"], "Object-oriented programming concepts."),
        ("IS105", "Web Systems and Technologies", 3, ["IS102"], ""),
        ("GE104", "Readings in Philippine History", 3, [], ""),
        ("GE105", "Purposive Communication", 3, [], ""),
        ("PE102", "Rhythmic Activities", 2, [], ""),
        ("NSTP102", "National Service Training Program 2", 3, ["NSTP101"], ""),
    ],
    "Year 2 - First Semester": [
        ("IS201", "Data Structures and Algorithms", 3, ["IS104"], "Core prerequisite for most 3rd-year IS courses."),
        ("IS202", "Platform Technologies", 3, ["IS101"], "Covers OS, hardware, and enterprise computing platforms."),
        ("IS203", "Organization and Management Concepts", 3, [], ""),
        ("IS204", "Fundamentals of Accounting for IS Majors", 3, [], ""),
        ("GE201", "The Contemporary World", 3, [], ""),
        ("GE202", "Art Appreciation", 3, [], ""),
        ("PE201", "Individual/Dual Sports", 2, [], ""),
    ],
    "Year 2 - Second Semester": [
        ("IS205", "Information Management 1", 3, ["IS201"], "Databases and data modeling; prerequisite for SAD and later systems courses."),
        ("IS206", "Human-Computer Interaction", 3, ["IS103"], ""),
        ("IS207", "Data Communications and Networking 1", 3, ["IS202"], ""),
        ("IS208", "Quantitative Methods", 3, ["GE101"], ""),
        ("GE203", "Science, Technology and Society", 3, [], ""),
        ("GE204", "Statistics and Probability", 3, ["GE101"], ""),
        ("PE202", "Team Sports", 2, [], ""),
    ],
    "Year 3 - First Semester": [
        ("IS301", "Systems Analysis and Design", 3, ["IS201", "IS205"], "Gateway course for the Capstone track."),
        ("IS302", "Applications Development and Emerging Technologies 1", 3, ["IS104", "IS205"], ""),
        ("IS303", "Business Process Management", 3, ["IS203"], ""),
        ("IS304", "IS Elective 1: Enterprise Systems", 3, ["IS205"], "Professional elective slot."),
        ("IS305", "IS Elective 2: IT Security Fundamentals", 3, ["IS207"], "Professional elective slot."),
        ("GE301", "Ethics", 3, [], ""),
        ("GE302", "Life and Works of Rizal", 3, [], ""),
    ],
    "Year 3 - Second Semester": [
        ("IS306", "Information Assurance and Security", 3, ["IS207"], ""),
        ("IS307", "Applications Development and Emerging Technologies 2", 3, ["IS302"], ""),
        ("IS308", "IS Project Management 1", 3, ["IS303"], ""),
        ("IS309", "Methods of Research in Computing", 3, [], "Requires Junior standing (at least 90 units earned)."),
        ("IS310", "IS Elective 3: Business Intelligence and Data Mining", 3, ["IS205"], "Professional elective slot."),
        ("GE303", "Foreign Language", 3, [], ""),
    ],
    "Year 3 - Summer Term": [
        ("IS311", "IS Strategy, Management and Acquisition", 3, ["IS308"], ""),
        ("IS312", "Social and Professional Issues in Computing", 3, [], "Requires Senior standing eligibility."),
    ],
    "Year 4 - First Semester": [
        ("IS401", "Capstone Project 1", 3, ["IS301", "IS309"], "Also requires at least 75% of the total curriculum completed."),
        ("IS402", "IS Project Management 2", 3, ["IS308"], ""),
        ("IS403", "IS Elective 4: Mobile and Web Application Development", 3, ["IS307"], "Professional elective slot."),
        ("IS404", "Technopreneurship", 3, [], ""),
        ("GE401", "Environmental Science", 3, [], ""),
    ],
    "Year 4 - Second Semester": [
        ("IS405", "Capstone Project 2", 3, ["IS401"], ""),
        ("IS406", "Practicum / On-the-Job Training", 6, ["IS401"], "486 hours; also requires completion of all Year 1-3 courses."),
        ("IS407", "Seminars and Field Trips", 1, [], ""),
    ],
}


def write_curriculum_files() -> None:
    CURRICULUM_DIR.mkdir(parents=True, exist_ok=True)
    course_index: dict[str, str] = {}
    for term, courses in TERMS.items():
        for code, title, _, _, _ in courses:
            course_index[code] = title

    for i, (term, courses) in enumerate(TERMS.items(), start=1):
        lines = [DISCLOSURE, ""]
        lines.append(f"BSIS Curriculum Checklist - {term}")
        lines.append("Program: Bachelor of Science in Information Systems (BSIS)")
        lines.append("Talibon Polytechnic College")
        lines.append("")
        lines.append(f"{'Code':<10}{'Course Title':<55}{'Units':<7}Prerequisite(s)")
        total_units = 0
        for code, title, units, prereqs, note in courses:
            total_units += units
            prereq_str = ", ".join(prereqs) if prereqs else "None"
            lines.append(f"{code:<10}{title:<55}{units:<7}{prereq_str}")
        lines.append("")
        lines.append(f"Total units this term: {total_units}")
        lines.append("")
        lines.append("Prerequisite notes:")
        any_notes = False
        for code, title, units, prereqs, note in courses:
            if prereqs or note:
                any_notes = True
                prereq_names = [f"{p} ({course_index.get(p, 'see earlier term')})" for p in prereqs]
                detail = f"requires {', '.join(prereq_names)}" if prereq_names else "no course prerequisite"
                extra = f" {note}" if note else ""
                lines.append(f"- {code} {title}: {detail}.{extra}")
        if not any_notes:
            lines.append("- No prerequisite courses this term.")

        fname = f"{i:02d}_" + term.lower().replace(" - ", "_").replace(" ", "_") + ".txt"
        (CURRICULUM_DIR / fname).write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote {fname}")


DESCRIPTION_GROUPS = {
    "course_descriptions_programming_and_systems.txt": [
        ("IS102", "Computer Programming 1 (Fundamentals of Programming)",
         "Introduces problem-solving through programming using variables, control structures, functions, and basic data types. Students write and debug small console programs."),
        ("IS104", "Computer Programming 2 (Intermediate Programming)",
         "Builds on IS102 with object-oriented programming: classes, objects, inheritance, and polymorphism, plus an intro to error handling."),
        ("IS201", "Data Structures and Algorithms",
         "Covers arrays, linked lists, stacks, queues, trees, and sorting/searching algorithms, with emphasis on choosing the right structure for a problem."),
        ("IS301", "Systems Analysis and Design",
         "Teaches requirements gathering, process modeling (DFDs, use cases), and translating business needs into system specifications."),
        ("IS302", "Applications Development and Emerging Technologies 1",
         "Hands-on application-building course; students design and implement a small multi-module software system."),
        ("IS307", "Applications Development and Emerging Technologies 2",
         "Continuation of IS302 with a focus on integrating emerging technologies (APIs, cloud services, or mobile platforms) into an application."),
        ("IS403", "IS Elective 4: Mobile and Web Application Development",
         "Elective focused on building deployable mobile or web applications end-to-end, including UI/UX considerations."),
    ],
    "course_descriptions_data_networks_security.txt": [
        ("IS205", "Information Management 1",
         "Covers relational database design, normalization, SQL, and an introduction to data modeling for information systems."),
        ("IS207", "Data Communications and Networking 1",
         "Introduces networking fundamentals: OSI/TCP-IP models, IP addressing, and basic network configuration."),
        ("IS306", "Information Assurance and Security",
         "Covers security fundamentals: confidentiality/integrity/availability, common threats, and basic risk management for information systems."),
        ("IS305", "IS Elective 2: IT Security Fundamentals",
         "Elective deep-dive into authentication, access control, and secure system design practices."),
        ("IS310", "IS Elective 3: Business Intelligence and Data Mining",
         "Elective covering data warehousing basics, OLAP concepts, and introductory data mining/analytics techniques for business decision-making."),
    ],
    "course_descriptions_is_management_and_capstone.txt": [
        ("IS103", "Fundamentals of Information Systems",
         "Foundational course distinguishing Information Systems from Computer Science/IT; covers the role of IS in organizations."),
        ("IS203", "Organization and Management Concepts",
         "Introduces organizational structures, management functions, and decision-making relevant to deploying IS in a business."),
        ("IS303", "Business Process Management",
         "Covers modeling, analyzing, and improving business processes, and how IS supports process automation."),
        ("IS308", "IS Project Management 1",
         "Introduces project management fundamentals (scope, schedule, cost) applied to IS/software projects."),
        ("IS402", "IS Project Management 2",
         "Advanced project management: risk management, stakeholder management, and agile approaches for IS projects."),
        ("IS304", "IS Elective 1: Enterprise Systems",
         "Elective covering ERP/enterprise system concepts and how large organizations integrate systems across departments."),
        ("IS311", "IS Strategy, Management and Acquisition",
         "Covers IT governance, sourcing/acquisition decisions, and aligning IS strategy with business strategy."),
        ("IS401", "Capstone Project 1",
         "First half of the two-term capstone: students form a team, propose a real-world IS project, and complete requirements/design."),
        ("IS405", "Capstone Project 2",
         "Second half of the capstone: students implement, test, and defend the system proposed in Capstone Project 1."),
        ("IS406", "Practicum / On-the-Job Training",
         "486-hour supervised work experience in an IS-related role at a partner company or organization."),
    ],
}


def write_description_files() -> None:
    CURRICULUM_DIR.mkdir(parents=True, exist_ok=True)
    for fname, entries in DESCRIPTION_GROUPS.items():
        lines = [DISCLOSURE, "", "BSIS Course Description Catalog (excerpt)", ""]
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

Capstone eligibility: enrollment in IS401 (Capstone Project 1) requires
completion of IS301 and IS309, plus at least 75% of total curriculum units
completed. Enrollment in IS406 (Practicum/OJT) requires completion of all
Year 1-3 courses and IS401.

Add/drop: students may add or drop a course only within the first two (2)
weeks of a regular semester (first week for the summer term), subject to
the Registrar's published academic calendar.
""",
}


def write_policy_files() -> None:
    POLICIES_DIR.mkdir(parents=True, exist_ok=True)
    for fname, body in POLICY_DOCS.items():
        content = DISCLOSURE + "\n" + body.strip() + "\n"
        (POLICIES_DIR / fname).write_text(content, encoding="utf-8")
        print(f"wrote {fname}")


if __name__ == "__main__":
    write_curriculum_files()
    write_description_files()
    write_policy_files()
