import uuid
from datetime import datetime, timezone


def _connect(db_path: str):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_alert(db_path, alert_type, severity, message, metric_name=None, metric_value=None, threshold=None):
    alert_id = str(uuid.uuid4())
    conn = _connect(db_path)
    with conn:
        conn.execute(
            """INSERT INTO alerts (id, type, severity, message, metric_name, metric_value, threshold, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (alert_id, alert_type, severity, message, metric_name, metric_value, threshold,
             datetime.now(timezone.utc).isoformat()),
        )
    conn.close()
    return alert_id


def get_active_alerts(db_path):
    conn = _connect(db_path)
    rows = conn.execute(
        """SELECT id, type, severity, message, metric_name, metric_value, threshold, created_at
           FROM alerts WHERE resolved = 0 ORDER BY created_at DESC"""
    ).fetchall()
    conn.close()
    return [{"id": r[0], "type": r[1], "severity": r[2], "message": r[3],
             "metric_name": r[4], "metric_value": r[5], "threshold": r[6], "created_at": r[7]} for r in rows]


def resolve_alert(db_path, alert_id):
    conn = _connect(db_path)
    with conn:
        conn.execute("UPDATE alerts SET resolved = 1 WHERE id = ?", (alert_id,))
    conn.close()


def check_thresholds(db_path, metrics, thresholds):
    created_alerts = []
    pass_rate = metrics.get("pass_rate")
    pass_rate_min = thresholds.get("pass_rate_min")
    if pass_rate is not None and pass_rate_min is not None and pass_rate < pass_rate_min:
        alert_id = create_alert(db_path, alert_type="pass_rate_drop", severity="critical",
            message=f"Pass rate {pass_rate:.1%} dropped below threshold {pass_rate_min:.1%}",
            metric_name="pass_rate", metric_value=pass_rate, threshold=pass_rate_min)
        created_alerts.append({"id": alert_id, "message": f"pass_rate {pass_rate:.1%} < {pass_rate_min:.1%}"})

    latency = metrics.get("avg_latency_ms")
    latency_max = thresholds.get("latency_max_ms")
    if latency is not None and latency_max is not None and latency > latency_max:
        alert_id = create_alert(db_path, alert_type="high_latency", severity="warning",
            message=f"Average latency {latency:.0f}ms exceeds threshold {latency_max:.0f}ms",
            metric_name="avg_latency_ms", metric_value=latency, threshold=latency_max)
        created_alerts.append({"id": alert_id, "message": f"latency {latency:.0f}ms > {latency_max:.0f}ms"})

    return created_alerts
