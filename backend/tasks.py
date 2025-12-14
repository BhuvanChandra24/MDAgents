# tasks.py
from crewai import Task

def create_tasks(query: str, agents: dict):
    """
    Create tasks that map to the MDAgents pipeline:

    0. Complexity check     → Moderator (GP)
    1. PCP round            → Primary care clinician
    2. Radiology round      → Radiologist
    3. Pathology round      → Pathologist
    4. Surgical round       → Surgeon
    5. Final integration    → Infectious disease / final decision specialist
    """

    complexity_check = Task(
        description=f"""
You must strictly answer with exactly one of these words:

Low
Moderate
High

Classify the medical query based on clinical complexity:

{query}
""".strip(),
        agent=agents["moderator"],
        expected_output="One word only: Low / Moderate / High",
    )

    low_case = Task(
        description=f"""
PRIMARY CARE CLINICIAN ROUND (PCP SOLO):

Case:
{query}

You are acting as a primary care clinician (PCP) for a LOW complexity case.

FORMAT STRICTLY:

• Updated Diagnosis:
(text)

• Reasoning:
(text explaining how you reached the diagnosis)
""".strip(),
        agent=agents["primary"],
        expected_output="Diagnosis + Reasoning in the above structured format.",
    )

    radiology = Task(
        description=f"""
RADIOLOGY ROUND (MDT / ICT):

Case:
{query}

You are a Radiologist in a multidisciplinary team.

FORMAT STRICTLY:

• Imaging Findings:
(text – what imaging would show, or how imaging helps)

• Reasoning:
(text explaining your interpretation and impact on diagnosis/management)
""".strip(),
        agent=agents["radiologist"],
        expected_output="Imaging Findings + Reasoning.",
    )

    pathology = Task(
        description=f"""
PATHOLOGY ROUND (MDT / ICT):

Case:
{query}

You are a Pathologist in a multidisciplinary team.

FORMAT STRICTLY:

• Pathology Findings:
(text – labs, biopsy, histology, other tests)

• Reasoning:
(text explaining how pathology supports or changes the diagnosis)
""".strip(),
        agent=agents["pathologist"],
        expected_output="Pathology Findings + Reasoning.",
    )

    surgery = Task(
        description=f"""
SURGERY ROUND (ICT – Surgical Assessment):

Case:
{query}

You are a Surgeon in the Integrated Care Team (ICT).

FORMAT STRICTLY:

• Surgical Assessment:
(text – need for surgery, urgency, risks, alternatives)

• Reasoning:
(text explaining your decision-making)
""".strip(),
        agent=agents["surgeon"],
        expected_output="Surgical Assessment + Reasoning.",
    )

    final_review = Task(
        description=f"""
FINAL INTEGRATION ROUND (ICT LEAD / INFECTIOUS DISEASE):

Combine ALL available team reports (PCP, Radiology, Pathology, Surgery if present)
and generate a final consolidated decision.

FORMAT STRICTLY:

• Final Diagnosis:
(text)

• Management Plan:
(text – investigations, treatment, monitoring, referrals)

• Justification:
(text – how you integrated the multidisciplinary inputs and why this plan is appropriate)
""".strip(),
        agent=agents["infectious"],
        expected_output="Final Diagnosis + Management Plan + Justification.",
    )

    return (
        complexity_check,  # index 0
        low_case,          # index 1
        radiology,         # index 2
        pathology,         # index 3
        surgery,           # index 4
        final_review,      # index 5
    )
