import sqlite3
import uuid
from collections import Counter
from datetime import datetime, timezone
from app.database import get_run
from app.tracing.store import get_spans_for_run

TIMEOUT_THRESHOLD_MS = 30000
LOOPING_THRESHOLD = 3


def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def tag_run(db_path: str, run_id: str, tag: str, source: str = "auto", confidence: float = 1.0):
    conn = _connect(db_path)
    with conn:
        conn.execute(
            "INSERT INTO failure_tags (id, run_id, tag, confidence, source, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), run_id, tag, confidence, source, datetime.now(timezone.utc).isoformat()),
        )
    conn.close()


def get_tags_for_run(db_path: str, run_id: str) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, run_id, tag, confidence, source, created_at FROM failure_tags WHERE run_id = ?", (run_id,)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "run_id": r[1], "tag": r[2], "confidence": r[3], "source": r[4], "created_at": r[5]} for r in rows]


def auto_tag_run(db_path: str, run_id: str):
    run = get_run(db_path, run_id)
    if not run:
        return
    spans = get_spans_for_run(db_path, run_id)

    latency = run.get("latency_ms") or 0
    if latency > TIMEOUT_THRESHOLD_MS:
        tag_run(db_path, run_id, "timeout")

    tool_counts = Counter(s["name"] for s in spans if s["type"] == "tool_call")
    for tool_name, count in tool_counts.items():
        if count > LOOPING_THRESHOLD:
            tag_run(db_path, run_id, "looping", confidence=min(count / 10.0, 1.0))
            break

    for span in spans:
        if span["type"] == "tool_call" and span.get("output_data") and "Error:" in str(span["output_data"]):
            tag_run(db_path, run_id, "schema_error")
            break

    for span in spans:
        if span["status"] == "error":
            tag_run(db_path, run_id, span.get("name", "unknown_error"))
            break


def get_failure_summary(db_path: str, limit: int = 20) -> list[dict]:
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT tag, COUNT(*) as count FROM failure_tags GROUP BY tag ORDER BY count DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [{"tag": r[0], "count": r[1]} for r in rows]
