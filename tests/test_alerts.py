from app.database import init_db
from app.monitoring.alerts import check_thresholds, create_alert, get_active_alerts, resolve_alert


def test_create_and_get_alert(tmp_db_path):
    init_db(tmp_db_path)
    alert_id = create_alert(tmp_db_path, alert_type="pass_rate_drop", severity="critical",
        message="Pass rate dropped below 70%", metric_name="pass_rate", metric_value=0.65, threshold=0.70)
    alerts = get_active_alerts(tmp_db_path)
    assert len(alerts) == 1
    assert alerts[0]["id"] == alert_id
    assert alerts[0]["severity"] == "critical"


def test_resolve_alert(tmp_db_path):
    init_db(tmp_db_path)
    alert_id = create_alert(tmp_db_path, alert_type="test", severity="warning", message="test")
    resolve_alert(tmp_db_path, alert_id)
    alerts = get_active_alerts(tmp_db_path)
    assert len(alerts) == 0


def test_check_thresholds_triggers_alert(tmp_db_path):
    init_db(tmp_db_path)
    alerts = check_thresholds(tmp_db_path, metrics={"pass_rate": 0.55, "avg_latency_ms": 100},
        thresholds={"pass_rate_min": 0.70, "latency_max_ms": 5000})
    assert len(alerts) == 1
    assert "pass_rate" in alerts[0]["message"]


def test_check_thresholds_no_alert(tmp_db_path):
    init_db(tmp_db_path)
    alerts = check_thresholds(tmp_db_path, metrics={"pass_rate": 0.90, "avg_latency_ms": 100},
        thresholds={"pass_rate_min": 0.70, "latency_max_ms": 5000})
    assert len(alerts) == 0
