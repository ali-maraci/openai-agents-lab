from app.evals.store import create_eval_run, complete_eval_run, save_case_result


def test_list_datasets(client):
    """GET /api/evals/datasets should list available datasets."""
    response = client.get("/api/evals/datasets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["datasets"], list)


def test_get_eval_not_found(client):
    """GET /api/evals/{id} should return 404 for unknown eval."""
    response = client.get("/api/evals/nonexistent")
    assert response.status_code == 404


def test_get_eval_detail(client, tmp_db_path):
    """GET /api/evals/{id} should return eval with case results."""
    eval_id = create_eval_run(tmp_db_path, dataset_name="test", total_cases=1)
    complete_eval_run(tmp_db_path, eval_id, passed=1, failed=0, avg_latency_ms=100.0)
    save_case_result(tmp_db_path, {
        "eval_run_id": eval_id,
        "case_id": "t_001",
        "input": "hello",
        "actual_output": "hi",
        "passed": True,
        "scores": {"exact_match": 1.0},
        "latency_ms": 100,
    })
    response = client.get(f"/api/evals/{eval_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset_name"] == "test"
    assert data["passed"] == 1
    assert len(data["case_results"]) == 1


def test_get_eval_summary(client, tmp_db_path):
    """GET /api/evals/summary should list eval runs."""
    create_eval_run(tmp_db_path, dataset_name="ds1", total_cases=5)
    create_eval_run(tmp_db_path, dataset_name="ds2", total_cases=3)
    response = client.get("/api/evals/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2


def test_start_eval_run_unknown_dataset(client):
    """POST /evals/run should 404 for unknown dataset."""
    response = client.post("/api/evals/run", json={"dataset": "nonexistent"})
    assert response.status_code == 404
