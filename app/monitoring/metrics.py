import sqlite3


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_run_stats(db_path: str) -> dict:
    conn = _connect(db_path)
    row = conn.execute("""
        SELECT COUNT(*) as total_runs,
               SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
               SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
               SUM(CASE WHEN status = 'guardrail_blocked' THEN 1 ELSE 0 END) as guardrail_blocked,
               AVG(latency_ms) as avg_latency_ms,
               SUM(input_tokens) as total_input_tokens,
               SUM(output_tokens) as total_output_tokens
        FROM runs
    """).fetchone()
    conn.close()
    return {
        "total_runs": row[0] or 0, "completed": row[1] or 0, "failed": row[2] or 0,
        "guardrail_blocked": row[3] or 0,
        "avg_latency_ms": round(row[4], 1) if row[4] else 0,
        "total_input_tokens": row[5] or 0, "total_output_tokens": row[6] or 0,
    }


def get_agent_distribution(db_path: str) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute("""
        SELECT final_agent as agent, COUNT(*) as count
        FROM runs WHERE final_agent IS NOT NULL
        GROUP BY final_agent ORDER BY count DESC
    """).fetchall()
    conn.close()
    return [{"agent": r[0], "count": r[1]} for r in rows]


def get_status_distribution(db_path: str) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute("SELECT status, COUNT(*) as count FROM runs GROUP BY status ORDER BY count DESC").fetchall()
    conn.close()
    return [{"status": r[0], "count": r[1]} for r in rows]


def get_latency_percentiles(db_path: str) -> dict:
    conn = _connect(db_path)
    rows = conn.execute("SELECT latency_ms FROM runs WHERE status = 'completed' AND latency_ms IS NOT NULL ORDER BY latency_ms").fetchall()
    conn.close()
    if not rows:
        return {"p50": 0, "p90": 0, "p99": 0}
    values = [r[0] for r in rows]
    n = len(values)
    return {"p50": values[int(n * 0.5)], "p90": values[int(n * 0.9)], "p99": values[min(int(n * 0.99), n - 1)]}


def get_runs_over_time(db_path: str, days: int = 7) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute("""
        SELECT DATE(started_at) as day, COUNT(*) as count,
               SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
               SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
        FROM runs WHERE started_at >= datetime('now', ?)
        GROUP BY DATE(started_at) ORDER BY day
    """, (f"-{days} days",)).fetchall()
    conn.close()
    return [{"day": r[0], "total": r[1], "completed": r[2], "failed": r[3]} for r in rows]
