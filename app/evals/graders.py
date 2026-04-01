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


async def rubric(case: dict, result: dict) -> float:
    """LLM-based scoring against a rubric. Returns score 0.0-1.0. Implemented in Task 5."""
    raise NotImplementedError("rubric grader not yet implemented")


async def trajectory(case: dict, result: dict) -> float:
    """Evaluate trace spans against expected trajectory. Implemented in Task 6."""
    raise NotImplementedError("trajectory grader not yet implemented")


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
