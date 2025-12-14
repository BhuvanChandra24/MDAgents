# # agents.py
# from crewai import Agent, LLM
# import os
# from dotenv import load_dotenv

# # Configure Gemini via crewai's LLM wrapper
# # Make sure GEMINI_API_KEY is set in your environment or .env
# # llm = LLM(
# #     model="gemini/gemini-2.0-flash",
# #     temperature=0.3
# # )
# import os

# from crewai import Agent

# import os

# llm = {
#     "model": "deepseek/deepseek-r1",
#     "provider": "openrouter",
#     "api_key": os.getenv("OPENROUTER_API_KEY"),
#     "base_url": "https://openrouter.ai/api/v1",
# }




# def create_agents():
#     """
#     Create all medical agents used in the MDAgents-style pipeline:

#     - moderator: classifies complexity (Low / Moderate / High)
#     - primary: Primary Care Clinician (PCP) → handles low complexity
#     - radiologist, pathologist, surgeon: MDT / ICT specialists
#     - infectious: acts as final integrator / decision-maker
#     """

#     moderator = Agent(
#         role="Moderator",
#         goal="Classify the medical query complexity as Low, Moderate or High.",
#         backstory=(
#             "A senior triage general practitioner who evaluates the difficulty of "
#             "each case and decides whether a solo PCP, MDT, or ICT structure is needed."
#         ),
#         llm=llm,
#     )

#     primary = Agent(
#         role="Primary Care Clinician (PCC)",
#         goal="Provide initial diagnosis and first-line management for low-complexity cases.",
#         backstory=(
#             "A general physician with broad clinical experience, able to handle "
#             "common acute problems and stable chronic conditions independently."
#         ),
#         llm=llm,
#     )

#     radiologist = Agent(
#         role="Radiologist",
#         goal="Interpret CT, MRI, ultrasound, and X-ray findings relevant to the case.",
#         backstory="Expert radiologist specializing in abdominal and thoracic imaging.",
#         llm=llm,
#     )

#     pathologist = Agent(
#         role="Pathologist",
#         goal="Analyse lab tests, biopsy reports, and pathological findings.",
#         backstory="Experienced clinical pathologist interpreting lab and tissue abnormalities.",
#         llm=llm,
#     )

#     surgeon = Agent(
#         role="Surgeon",
#         goal="Evaluate the need for surgical or interventional procedures.",
#         backstory="A gastrointestinal and trauma surgeon assessing operative requirements.",
#         llm=llm,
#     )

#     infectious = Agent(
#         role="Infectious Disease / Final Decision Specialist",
#         goal=(
#             "Integrate all agent outputs (PCP, MDT, ICT) into a final diagnosis and "
#             "management plan with clear justification."
#         ),
#         backstory=(
#             "Acts as the Integrated Care Team lead, combining multidisciplinary inputs "
#             "and producing a final, educational report."
#         ),
#         llm=llm,
#     )

#     return {
#         "moderator": moderator,
#         "primary": primary,
#         "radiologist": radiologist,
#         "pathologist": pathologist,
#         "surgeon": surgeon,
#         "infectious": infectious,
#     }
# agents.py
import os
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="openrouter/deepseek/deepseek-r1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0.3,
    max_tokens=2048   # <<< VERY IMPORTANT
)


def create_agents():

    moderator = Agent(
        role="Moderator",
        goal="Classify the complexity of the medical query.",
        backstory="Experienced triage doctor.",
        llm=llm,
    )

    primary = Agent(
        role="Primary Care Physician",
        goal="Handle low-complexity medical cases.",
        backstory="General physician skilled in primary care.",
        llm=llm,
    )

    radiologist = Agent(
        role="Radiologist",
        goal="Interpret radiology clues.",
        backstory="Expert radiologist.",
        llm=llm,
    )

    pathologist = Agent(
        role="Pathologist",
        goal="Analyse labs and pathology.",
        backstory="Clinical pathology expert.",
        llm=llm,
    )

    surgeon = Agent(
        role="Surgeon",
        goal="Determine surgical/interventional needs.",
        backstory="Trauma and GI surgeon.",
        llm=llm,
    )

    infectious = Agent(
        role="Infectious Disease Specialist",
        goal="Integrate MDT outputs into final medical reasoning.",
        backstory="ICT leader doctor.",
        llm=llm,
    )

    return {
        "moderator": moderator,
        "primary": primary,
        "radiologist": radiologist,
        "pathologist": pathologist,
        "surgeon": surgeon,
        "infectious": infectious,
    }
