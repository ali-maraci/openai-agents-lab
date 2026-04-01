REGRESSION_THRESHOLD = 0.05


def compare_eval_runs(baseline: dict, candidate: dict) -> dict:
    """Compare aggregate metrics between baseline and candidate eval runs."""
    b_rate = baseline.get("pass_rate") or 0.0
    c_rate = candidate.get("pass_rate") or 0.0
    b_latency = baseline.get("avg_latency_ms") or 0.0
    c_latency = candidate.get("avg_latency_ms") or 0.0

    pass_rate_delta = c_rate - b_rate
    latency_delta = c_latency - b_latency
    regression = pass_rate_delta < -REGRESSION_THRESHOLD

    return {
        "baseline_pass_rate": b_rate,
        "candidate_pass_rate": c_rate,
        "pass_rate_delta": pass_rate_delta,
        "baseline_latency_ms": b_latency,
        "candidate_latency_ms": c_latency,
        "latency_delta_ms": latency_delta,
        "regression": regression,
    }


def compare_cases(baseline_cases: list[dict], candidate_cases: list[dict]) -> dict:
    """Compare individual case results to identify regressions and fixes."""
    baseline_by_id = {c["case_id"]: c for c in baseline_cases}
    candidate_by_id = {c["case_id"]: c for c in candidate_cases}

    regressed = []
    fixed = []
    unchanged = []

    all_case_ids = sorted(set(list(baseline_by_id.keys()) + list(candidate_by_id.keys())))

    for case_id in all_case_ids:
        b = baseline_by_id.get(case_id)
        c = candidate_by_id.get(case_id)
        if b is None or c is None:
            continue
        b_passed = bool(b.get("passed"))
        c_passed = bool(c.get("passed"))
        if b_passed and not c_passed:
            regressed.append(case_id)
        elif not b_passed and c_passed:
            fixed.append(case_id)
        else:
            unchanged.append(case_id)

    return {"regressed": regressed, "fixed": fixed, "unchanged": unchanged}
