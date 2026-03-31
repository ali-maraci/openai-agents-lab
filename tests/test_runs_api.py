from app.database import create_run, complete_run
from app.tracing.store import save_span


def test_list_runs_empty(client):
    response = client.get("/api/runs")
    assert response.status_code == 200
    data = response.json()
    assert data["runs"] == []
    assert data["count"] == 0


def test_list_runs_with_data(client, tmp_db_path):
    run_id = create_run(tmp_db_path, session_id="s1", input_text="hello")
    complete_run(tmp_db_path, run_id, output="world", status="completed")
    response = client.get("/api/runs")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["runs"][0]["id"] == run_id


def test_get_run_not_found(client):
    response = client.get("/api/runs/nonexistent")
    assert response.status_code == 404


def test_get_run_detail(client, tmp_db_path):
    run_id = create_run(tmp_db_path, session_id="s1", input_text="test")
    complete_run(tmp_db_path, run_id, output="result", status="completed", final_agent="General Agent")
    response = client.get(f"/api/runs/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == run_id
    assert data["output"] == "result"
    assert data["final_agent"] == "General Agent"


def test_get_run_detail_includes_spans(client, tmp_db_path):
    """GET /api/runs/{id} should include trace spans."""
    run_id = create_run(tmp_db_path, session_id="s1", input_text="test")
    save_span(tmp_db_path, {
        "run_id": run_id,
        "type": "agent_handoff",
        "name": "Triage Agent → Math Agent",
        "started_at": "2026-03-31T10:00:00Z",
        "status": "ok",
    })
    response = client.get(f"/api/runs/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert "spans" in data
    assert len(data["spans"]) == 1
    assert data["spans"][0]["type"] == "agent_handoff"
