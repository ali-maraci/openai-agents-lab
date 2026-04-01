import inspect
import logging
import time

from agents import Runner

from app.agents.definitions import triage_agent
from app.database import create_run, complete_run
from app.evals.datasets import load_dataset
from app.evals.graders import get_grader
from app.evals.store import (
    create_eval_run,
    complete_eval_run,
    save_case_result,
)

logger = logging.getLogger(__name__)


async def execute_case(case: dict, db_path: str, agent=None) -> dict:
    """Execute a single benchmark case against the agent.
    Returns dict with: run_id, output, agent, latency_ms, and optionally error.
    """
    if agent is None:
        agent = triage_agent
    run_id = create_run(db_path, session_id="eval", input_text=case["input"])
    start = time.monotonic()
    try:
        result = await Runner.run(agent, input=case["input"])
        latency_ms = int((time.monotonic() - start) * 1000)
        output = str(result.final_output) if result.final_output else ""
        agent_name = result.last_agent.name if result.last_agent else None
        complete_run(db_path, run_id, output=output, status="completed", final_agent=agent_name)
        return {
            "run_id": run_id,
            "output": output,
            "agent": agent_name,
            "latency_ms": latency_ms,
        }
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        complete_run(db_path, run_id, output="", status="failed")
        logger.error("Eval case %s failed: %s", case.get("id"), e)
        return {
            "run_id": run_id,
            "output": "",
            "agent": None,
            "latency_ms": latency_ms,
            "error": str(e),
        }


async def run_eval(
    dataset_name: str,
    db_path: str,
    benchmarks_dir: str = "benchmarks",
    eval_id: str | None = None,
    agent=None,
) -> str:
    """Run a full eval: load dataset, execute all cases, grade, store results. Returns eval run ID."""
    dataset = load_dataset(dataset_name, benchmarks_dir=benchmarks_dir)
    cases = dataset["cases"]
    grader_names = dataset["graders"]
    graders = [(name, get_grader(name)) for name in grader_names]

    if eval_id is None:
        eval_id = create_eval_run(db_path, dataset_name=dataset_name, total_cases=len(cases))

    passed = 0
    failed = 0
    total_latency = 0

    for case in cases:
        result = await execute_case(case, db_path, agent=agent)
        total_latency += result.get("latency_ms", 0)

        # Apply graders
        scores = {}
        for grader_name, grader_fn in graders:
            if inspect.iscoroutinefunction(grader_fn):
                score = await grader_fn(case, result)
            else:
                score = grader_fn(case, result)
            scores[grader_name] = score

        # A case passes if all grader scores are >= 0.5
        case_passed = all(s >= 0.5 for s in scores.values())
        if case_passed:
            passed += 1
        else:
            failed += 1

        save_case_result(db_path, {
            "eval_run_id": eval_id,
            "case_id": case["id"],
            "input": case["input"],
            "expected_output": case.get("expected_output"),
            "actual_output": result.get("output"),
            "expected_agent": case.get("expected_agent"),
            "actual_agent": result.get("agent"),
            "run_id": result.get("run_id"),
            "passed": case_passed,
            "scores": scores,
            "latency_ms": result.get("latency_ms"),
            "error": result.get("error"),
        })

    avg_latency = total_latency / len(cases) if cases else 0
    complete_eval_run(db_path, eval_id, passed=passed, failed=failed, avg_latency_ms=avg_latency)
    return eval_id
