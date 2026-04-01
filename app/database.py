import sqlite3
import uuid
from datetime import datetime, timezone


def _row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str) -> None:
    conn = _connect(db_path)
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                input TEXT NOT NULL,
                output TEXT,
                status TEXT NOT NULL DEFAULT 'running',
                final_agent TEXT,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                latency_ms INTEGER,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS trace_spans (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL REFERENCES runs(id),
                parent_span_id TEXT,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_ms INTEGER,
                input_data TEXT,
                output_data TEXT,
                status TEXT NOT NULL DEFAULT 'ok',
                error_message TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_spans_run_id ON trace_spans(run_id);
            CREATE INDEX IF NOT EXISTS idx_runs_session ON runs(session_id);
            CREATE INDEX IF NOT EXISTS idx_runs_started ON runs(started_at);

            CREATE TABLE IF NOT EXISTS eval_runs (
                id TEXT PRIMARY KEY,
                dataset_name TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                status TEXT NOT NULL DEFAULT 'running',
                total_cases INTEGER DEFAULT 0,
                passed INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                pass_rate REAL,
                avg_latency_ms REAL
            );

            CREATE TABLE IF NOT EXISTS eval_case_results (
                id TEXT PRIMARY KEY,
                eval_run_id TEXT NOT NULL REFERENCES eval_runs(id),
                case_id TEXT NOT NULL,
                input TEXT NOT NULL,
                expected_output TEXT,
                actual_output TEXT,
                expected_agent TEXT,
                actual_agent TEXT,
                run_id TEXT,
                passed INTEGER NOT NULL DEFAULT 0,
                scores TEXT,
                latency_ms INTEGER,
                error TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_eval_case_run ON eval_case_results(eval_run_id);
            CREATE INDEX IF NOT EXISTS idx_eval_runs_dataset ON eval_runs(dataset_name);

            CREATE TABLE IF NOT EXISTS agent_versions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                agent_config TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                dataset_name TEXT NOT NULL,
                baseline_version_id TEXT NOT NULL REFERENCES agent_versions(id),
                candidate_version_id TEXT NOT NULL REFERENCES agent_versions(id),
                baseline_eval_id TEXT REFERENCES eval_runs(id),
                candidate_eval_id TEXT REFERENCES eval_runs(id),
                status TEXT NOT NULL DEFAULT 'running',
                started_at TEXT NOT NULL,
                completed_at TEXT,
                result TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_agent_versions_name ON agent_versions(name);
            CREATE INDEX IF NOT EXISTS idx_experiments_dataset ON experiments(dataset_name);

            CREATE TABLE IF NOT EXISTS failure_tags (
                id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL REFERENCES runs(id),
                tag TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT NOT NULL DEFAULT 'auto',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                severity TEXT NOT NULL DEFAULT 'warning',
                message TEXT NOT NULL,
                metric_name TEXT,
                metric_value REAL,
                threshold REAL,
                resolved INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_failure_tags_run ON failure_tags(run_id);
            CREATE INDEX IF NOT EXISTS idx_failure_tags_tag ON failure_tags(tag);
            CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON alerts(resolved);
        """)
    conn.close()


def create_run(db_path: str, session_id: str, input_text: str) -> str:
    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()
    conn = _connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO runs (id, session_id, input, status, started_at) VALUES (?, ?, ?, 'running', ?)",
            (run_id, session_id, input_text, started_at),
        )
    conn.close()
    return run_id


def complete_run(
    db_path: str,
    run_id: str,
    output: str,
    status: str,
    final_agent: str | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> None:
    completed_at = datetime.now(timezone.utc).isoformat()
    conn = _connect(db_path)
    with conn:
        row = conn.execute("SELECT started_at FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            conn.close()
            raise ValueError(f"Run {run_id!r} not found")
        started_at_str = row[0]
        started_at = datetime.fromisoformat(started_at_str)
        completed_dt = datetime.fromisoformat(completed_at)
        latency_ms = int((completed_dt - started_at).total_seconds() * 1000)
        conn.execute(
            """UPDATE runs
               SET output = ?, status = ?, final_agent = ?, completed_at = ?,
                   latency_ms = ?, input_tokens = ?, output_tokens = ?
               WHERE id = ?""",
            (output, status, final_agent, completed_at, latency_ms, input_tokens, output_tokens, run_id),
        )
    conn.close()


def get_run(db_path: str, run_id: str) -> dict | None:
    conn = _connect(db_path)
    cursor = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row) if row is not None else None
    conn.close()
    return result


def cleanup_expired_sessions(db_path: str, expiry_days: int) -> None:
    """Delete sessions older than expiry_days."""
    import logging
    conn = _connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='agent_sessions'"
        )
        if not cursor.fetchone():
            return
        result = conn.execute(
            f"DELETE FROM agent_sessions WHERE updated_at < datetime('now', '-{expiry_days} days')"
        )
        deleted = result.rowcount
        conn.execute(
            "DELETE FROM agent_messages WHERE session_id NOT IN (SELECT session_id FROM agent_sessions)"
        )
        conn.commit()
        if deleted > 0:
            logging.getLogger(__name__).info("Cleaned up %d expired sessions", deleted)
    finally:
        conn.close()


def list_runs(db_path: str, limit: int = 50, offset: int = 0) -> list[dict]:
    conn = _connect(db_path)
    cursor = conn.execute(
        "SELECT * FROM runs ORDER BY started_at DESC LIMIT ? OFFSET ?",
        (limit, offset),
    )
    rows = cursor.fetchall()
    result = [_row_to_dict(cursor, row) for row in rows]
    conn.close()
    return result
