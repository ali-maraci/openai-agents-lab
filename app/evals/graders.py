from pydantic import BaseModel
from agents import Agent, Runner


class GraderError(Exception):
    pass


def exact_match(case: dict, result: dict) -> float:
    """Score 1.0 if output exactly matches expected (case-insensitive, stripped). Skips if no expected_output."""
    expected = case.get("expected_output")
    if expected is None:
        return 1.0
    actual = result.get("output", "")
    return 1.0 if str(expected).strip().lower() == str(actual).strip().lower() else 0.0


def agent_match(case: dict, result: dict) -> float:
    """Score 1.0 if the agent that handled the request matches expected_agent. Skips if no expected_agent."""
    expected = case.get("expected_agent")
    if expected is None:
        return 1.0
    actual = result.get("agent")
    return 1.0 if expected == actual else 0.0


def contains(case: dict, result: dict) -> float:
    """Score 1.0 if expected_output is a substring of the actual output. Skips if no expected_output."""
    expected = case.get("expected_output")
    if expected is None:
        return 1.0
    actual = result.get("output", "")
    return 1.0 if str(expected) in str(actual) else 0.0


class RubricScore(BaseModel):
    score: float
    reasoning: str


_rubric_grader_agent = Agent(
    name="Rubric_Grader",
    instructions=(
        "You are an evaluation grader. You will be given:\n"
        "1. A user's question\n"
        "2. An agent's response\n"
        "3. A grading rubric\n\n"
        "Score the response from 0.0 to 1.0 based on how well it meets the rubric.\n"
        "- 1.0 = fully meets all criteria\n"
        "- 0.5 = partially meets criteria\n"
        "- 0.0 = does not meet criteria at all\n\n"
        "Be fair but strict. Provide brief reasoning."
    ),
    output_type=RubricScore,
)


async def rubric(case: dict, result: dict) -> float:
    """LLM-based scoring against a rubric. Returns score 0.0-1.0."""
    rubric_text = case.get("rubric")
    if rubric_text is None:
        return 1.0
    prompt = (
        f"Question: {case.get('input', '')}\n\n"
        f"Agent Response: {result.get('output', '')}\n\n"
        f"Rubric: {rubric_text}\n\n"
        "Score this response."
    )
    grader_result = await Runner.run(_rubric_grader_agent, prompt)
    score = grader_result.final_output.score
    return max(0.0, min(1.0, score))


def _span_matches_step(span: dict, step: dict) -> bool:
    """Check if a span matches an expected trajectory step."""
    if "type" in step and span.get("type") != step["type"]:
        return False
    if "name" in step and span.get("name") != step["name"]:
        return False
    if "name_contains" in step and step["name_contains"] not in span.get("name", ""):
        return False
    return True


async def trajectory(case: dict, result: dict) -> float:
    """Evaluate trace spans against expected trajectory.
    Each expected step can specify:
    - type: must match span type exactly
    - name: must match span name exactly
    - name_contains: span name must contain this substring
    """
    expected = case.get("expected_trajectory")
    if expected is None:
        return 1.0
    spans = result.get("spans", [])
    if not expected:
        return 1.0

    matched = 0
    span_idx = 0
    for step in expected:
        found = False
        while span_idx < len(spans):
            span = spans[span_idx]
            span_idx += 1
            if _span_matches_step(span, step):
                found = True
                break
        if found:
            matched += 1
    return matched / len(expected)


GRADER_REGISTRY: dict[str, callable] = {
    "exact_match": exact_match,
    "agent_match": agent_match,
    "contains": contains,
    "rubric": rubric,
    "trajectory": trajectory,
}


def get_grader(name: str) -> callable:
    """Look up a grader by name."""
    if name not in GRADER_REGISTRY:
        raise GraderError(f"Unknown grader: '{name}'. Available: {list(GRADER_REGISTRY.keys())}")
    return GRADER_REGISTRY[name]
