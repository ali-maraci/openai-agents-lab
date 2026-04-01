from app.experiments.runner import create_experiment
from app.versioning.registry import snapshot_current


def test_get_experiment_not_found(client):
    response = client.get("/api/experiments/nonexistent")
    assert response.status_code == 404


def test_get_experiment_detail(client, tmp_db_path):
    baseline_id = snapshot_current(tmp_db_path, name="baseline")
    candidate_id = snapshot_current(tmp_db_path, name="candidate")
    exp_id = create_experiment(tmp_db_path, "test_ds", baseline_id, candidate_id)
    response = client.get(f"/api/experiments/{exp_id}")
    assert response.status_code == 200
    assert response.json()["dataset_name"] == "test_ds"
