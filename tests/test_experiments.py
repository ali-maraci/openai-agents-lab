import pytest
from app.experiments.compare import compare_eval_runs, compare_cases


def test_compare_no_regression():
    baseline = {"pass_rate": 0.8, "avg_latency_ms": 200, "passed": 8, "failed": 2, "total_cases": 10}
    candidate = {"pass_rate": 0.9, "avg_latency_ms": 180, "passed": 9, "failed": 1, "total_cases": 10}
    result = compare_eval_runs(baseline, candidate)
    assert result["regression"] is False
    assert result["pass_rate_delta"] == pytest.approx(0.1)
    assert result["latency_delta_ms"] == pytest.approx(-20.0)


def test_compare_regression_detected():
    baseline = {"pass_rate": 0.9, "avg_latency_ms": 200, "passed": 9, "failed": 1, "total_cases": 10}
    candidate = {"pass_rate": 0.6, "avg_latency_ms": 250, "passed": 6, "failed": 4, "total_cases": 10}
    result = compare_eval_runs(baseline, candidate)
    assert result["regression"] is True
    assert result["pass_rate_delta"] == pytest.approx(-0.3)


def test_compare_marginal_drop_no_regression():
    baseline = {"pass_rate": 0.8, "avg_latency_ms": 200, "passed": 8, "failed": 2, "total_cases": 10}
    candidate = {"pass_rate": 0.77, "avg_latency_ms": 210, "passed": 7, "failed": 3, "total_cases": 10}
    result = compare_eval_runs(baseline, candidate)
    assert result["regression"] is False


def test_compare_per_case():
    baseline_cases = [
        {"case_id": "t_001", "passed": 1, "scores": '{"agent_match": 1.0}'},
        {"case_id": "t_002", "passed": 1, "scores": '{"agent_match": 1.0}'},
        {"case_id": "t_003", "passed": 0, "scores": '{"agent_match": 0.0}'},
    ]
    candidate_cases = [
        {"case_id": "t_001", "passed": 1, "scores": '{"agent_match": 1.0}'},
        {"case_id": "t_002", "passed": 0, "scores": '{"agent_match": 0.0}'},
        {"case_id": "t_003", "passed": 1, "scores": '{"agent_match": 1.0}'},
    ]
    diff = compare_cases(baseline_cases, candidate_cases)
    assert len(diff["regressed"]) == 1
    assert diff["regressed"][0] == "t_002"
    assert len(diff["fixed"]) == 1
    assert diff["fixed"][0] == "t_003"
