# crew_runner.py
from crewai import Crew
from agents import create_agents
from tasks import create_tasks


def extract_output(result) -> str:
    """
    Normalize CrewAI result object to a plain string.
    Handles both dict- and list-based task outputs.
    """
    if hasattr(result, "tasks_output"):
        data = result.tasks_output

        # Crew v2 style: dict of task_name -> {output: "..."}
        if isinstance(data, dict):
            first_key = list(data.keys())[0]
            return (data[first_key].get("output", "") or "").strip()

        # Older / alternate: list of task result objects or dicts
        if isinstance(data, list) and data:
            item = data[0]
            if isinstance(item, dict) and "output" in item:
                return (item["output"] or "").strip()
            return str(item).strip()

    # Fallback: just cast to string
    return str(result).strip()


def run_mdagents(query: str) -> dict:
    """
    Core MDAgents-style pipeline, mapped to your code:
    """

    agents = create_agents()
    tasks = create_tasks(query, agents)

    # STEP 1 — Complexity classification
    comp_crew = Crew(
        agents=[agents["moderator"]],
        tasks=[tasks[0]],
        verbose=False,
    )
    complexity_raw = extract_output(comp_crew.kickoff())
    complexity = (complexity_raw or "UNKNOWN").upper()

    if "LOW" in complexity:
        level = "LOW"
        active_tasks = [tasks[1]]
    elif "MODERATE" in complexity:
        level = "MODERATE"
        active_tasks = [tasks[1], tasks[2], tasks[3]]
    else:
        level = "HIGH"
        active_tasks = [tasks[1], tasks[2], tasks[3], tasks[4]]

    # STEP 2 — Reasoning rounds
    reasoning_summaries: list[str] = []

    for task in active_tasks:
        crew_team = Crew(
            agents=list(agents.values()),
            tasks=[task],
            verbose=False,
        )
        result_str = extract_output(crew_team.kickoff())

        parts = [p.strip() for p in result_str.split(".") if p.strip()]
        short_reason = ". ".join(parts[:2])
        if short_reason:
            reasoning_summaries.append(short_reason)

    # STEP 3 — Final integration
    final_crew = Crew(
        agents=[agents["infectious"]],
        tasks=[tasks[-1]],
        verbose=False,
    )
    final_answer = extract_output(final_crew.kickoff())

    return {
        "final": final_answer,
        "reasoning": reasoning_summaries,
        "complexity": level,
    }
