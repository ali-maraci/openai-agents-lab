from app.database import init_db, create_run, complete_run
from app.monitoring.alerts import create_alert


def test_get_dashboard_metrics(client, tmp_db_path):
    for i in range(3):
        run_id = create_run(tmp_db_path, session_id=f"s{i}", input_text=f"msg{i}")
        complete_run(tmp_db_path, run_id, output=f"out{i}", status="completed", final_agent="General Agent")
    response = client.get("/api/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["run_stats"]["total_runs"] == 3
    assert data["run_stats"]["completed"] == 3
    assert isinstance(data["agent_distribution"], list)


def test_get_dashboard_failures(client):
    response = client.get("/api/dashboard/failures")
    assert response.status_code == 200
    assert "failure_summary" in response.json()


def test_get_dashboard_alerts(client):
    response = client.get("/api/dashboard/alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()


def test_resolve_alert(client, tmp_db_path):
    alert_id = create_alert(tmp_db_path, alert_type="test", severity="warning", message="test alert")
    response = client.post(f"/api/dashboard/alerts/{alert_id}/resolve")
    assert response.status_code == 200
    alerts = client.get("/api/dashboard/alerts").json()["alerts"]
    assert len(alerts) == 0
