import json
from app.database import init_db
from app.evals.store import (
    create_eval_run,
    complete_eval_run,
    save_case_result,
    get_eval_run,
    get_eval_case_results,
    list_eval_runs,
)


def test_create_and_get_eval_run(tmp_db_path):
    init_db(tmp_db_path)
    eval_id = create_eval_run(tmp_db_path, dataset_name="tool_routing", total_cases=10)
    run = get_eval_run(tmp_db_path, eval_id)
    assert run is not None
    assert run["dataset_name"] == "tool_routing"
    assert run["total_cases"] == 10
    assert run["status"] == "running"


def test_complete_eval_run(tmp_db_path):
    init_db(tmp_db_path)
    eval_id = create_eval_run(tmp_db_path, dataset_name="test", total_cases=3)
    complete_eval_run(tmp_db_path, eval_id, passed=2, failed=1, avg_latency_ms=150.0)
    run = get_eval_run(tmp_db_path, eval_id)
    assert run["status"] == "completed"
    assert run["passed"] == 2
    assert run["failed"] == 1
    assert abs(run["pass_rate"] - 0.6667) < 0.01
    assert run["avg_latency_ms"] == 150.0


def test_save_and_get_case_results(tmp_db_path):
    init_db(tmp_db_path)
    eval_id = create_eval_run(tmp_db_path, dataset_name="test", total_cases=2)
    save_case_result(tmp_db_path, {
        "eval_run_id": eval_id,
        "case_id": "t_001",
        "input": "What is 2+2?",
        "expected_agent": "Math_Conversion_Agent",
        "actual_agent": "Math_Conversion_Agent",
        "actual_output": "4",
        "passed": True,
        "scores": {"agent_match": 1.0},
        "latency_ms": 100,
    })
    save_case_result(tmp_db_path, {
        "eval_run_id": eval_id,
        "case_id": "t_002",
        "input": "Hello",
        "expected_agent": "General Agent",
        "actual_agent": "History Agent",
        "actual_output": "Hi there",
        "passed": False,
        "scores": {"agent_match": 0.0},
        "latency_ms": 200,
    })
    results = get_eval_case_results(tmp_db_path, eval_id)
    assert len(results) == 2
    assert results[0]["case_id"] == "t_001"
    assert results[0]["passed"] == 1
    scores = json.loads(results[0]["scores"])
    assert scores["agent_match"] == 1.0


def test_list_eval_runs(tmp_db_path):
    init_db(tmp_db_path)
    create_eval_run(tmp_db_path, dataset_name="ds1", total_cases=5)
    create_eval_run(tmp_db_path, dataset_name="ds2", total_cases=3)
    runs = list_eval_runs(tmp_db_path)
    assert len(runs) == 2
    assert runs[0]["dataset_name"] == "ds2"
