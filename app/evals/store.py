import json
import sqlite3
import uuid
from datetime import datetime, timezone


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _row_to_dict(cursor: sqlite3.Cursor, row: tuple) -> dict:
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


def create_eval_run(db_path: str, dataset_name: str, total_cases: int) -> str:
    """Create a new eval run. Returns the eval run ID."""
    eval_id = str(uuid.uuid4())
    conn = _connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO eval_runs (id, dataset_name, started_at, status, total_cases) VALUES (?, ?, ?, 'running', ?)",
            (eval_id, dataset_name, datetime.now(timezone.utc).isoformat(), total_cases),
        )
    conn.close()
    return eval_id


def complete_eval_run(db_path: str, eval_id: str, passed: int, failed: int, avg_latency_ms: float) -> None:
    """Mark an eval run as completed with aggregate metrics."""
    total = passed + failed
    pass_rate = passed / total if total > 0 else 0.0
    conn = _connect(db_path)
    with conn:
        conn.execute(
            """UPDATE eval_runs
               SET status = 'completed', completed_at = ?, passed = ?, failed = ?,
                   pass_rate = ?, avg_latency_ms = ?
               WHERE id = ?""",
            (datetime.now(timezone.utc).isoformat(), passed, failed, pass_rate, avg_latency_ms, eval_id),
        )
    conn.close()


def save_case_result(db_path: str, result: dict) -> None:
    """Save a single eval case result."""
    result_id = str(uuid.uuid4())
    scores_json = json.dumps(result.get("scores", {}))
    conn = _connect(db_path)
    with conn:
        conn.execute(
            """INSERT INTO eval_case_results
               (id, eval_run_id, case_id, input, expected_output, actual_output,
                expected_agent, actual_agent, run_id, passed, scores, latency_ms, error)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result_id,
                result["eval_run_id"],
                result["case_id"],
                result["input"],
                result.get("expected_output"),
                result.get("actual_output"),
                result.get("expected_agent"),
                result.get("actual_agent"),
                result.get("run_id"),
                1 if result.get("passed") else 0,
                scores_json,
                result.get("latency_ms"),
                result.get("error"),
            ),
        )
    conn.close()


def get_eval_run(db_path: str, eval_id: str) -> dict | None:
    """Get a single eval run by ID."""
    conn = _connect(db_path)
    cursor = conn.execute("SELECT * FROM eval_runs WHERE id = ?", (eval_id,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row) if row else None
    conn.close()
    return result


def get_eval_case_results(db_path: str, eval_id: str) -> list[dict]:
    """Get all case results for an eval run."""
    conn = _connect(db_path)
    conn.row_factory = _row_to_dict
    rows = conn.execute(
        "SELECT * FROM eval_case_results WHERE eval_run_id = ? ORDER BY case_id",
        (eval_id,),
    ).fetchall()
    conn.close()
    return rows


def list_eval_runs(db_path: str, limit: int = 50) -> list[dict]:
    """List eval runs, most recent first."""
    conn = _connect(db_path)
    conn.row_factory = _row_to_dict
    rows = conn.execute(
        "SELECT * FROM eval_runs ORDER BY started_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return rows
