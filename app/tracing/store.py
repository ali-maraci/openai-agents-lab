import sqlite3
import uuid


def save_span(db_path: str, span: dict):
    """Save a single trace span to the database."""
    span_id = span.get("id", str(uuid.uuid4()))
    conn = sqlite3.connect(db_path)
    conn.execute(
        """INSERT INTO trace_spans
           (id, run_id, parent_span_id, type, name, started_at, completed_at,
            duration_ms, input_data, output_data, status, error_message)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            span_id,
            span["run_id"],
            span.get("parent_span_id"),
            span["type"],
            span["name"],
            span["started_at"],
            span.get("completed_at"),
            span.get("duration_ms"),
            span.get("input_data"),
            span.get("output_data"),
            span.get("status", "ok"),
            span.get("error_message"),
        ),
    )
    conn.commit()
    conn.close()


def _row_to_dict(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


def get_spans_for_run(db_path: str, run_id: str) -> list[dict]:
    """Get all trace spans for a run, ordered by start time."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = _row_to_dict
    rows = conn.execute(
        "SELECT * FROM trace_spans WHERE run_id = ? ORDER BY started_at",
        (run_id,),
    ).fetchall()
    conn.close()
    return rows
