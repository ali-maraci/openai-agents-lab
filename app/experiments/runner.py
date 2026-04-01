import json
import logging
import uuid
from datetime import datetime, timezone

from app.evals.runner import run_eval
from app.evals.store import get_eval_run, get_eval_case_results
from app.experiments.compare import compare_eval_runs, compare_cases

logger = logging.getLogger(__name__)


def _connect(db_path: str):
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _row_to_dict(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}


def create_experiment(db_path: str, dataset_name: str, baseline_version_id: str, candidate_version_id: str) -> str:
    """Create a new experiment record. Returns experiment ID."""
    exp_id = str(uuid.uuid4())
    conn = _connect(db_path)
    with conn:
        conn.execute(
            """INSERT INTO experiments
               (id, dataset_name, baseline_version_id, candidate_version_id, status, started_at)
               VALUES (?, ?, ?, ?, 'running', ?)""",
            (exp_id, dataset_name, baseline_version_id, candidate_version_id,
             datetime.now(timezone.utc).isoformat()),
        )
    conn.close()
    return exp_id


def get_experiment(db_path: str, exp_id: str) -> dict | None:
    conn = _connect(db_path)
    cursor = conn.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,))
    row = cursor.fetchone()
    result = _row_to_dict(cursor, row) if row else None
    conn.close()
    return result


async def run_experiment(
    db_path: str,
    dataset_name: str,
    baseline_version_id: str,
    candidate_version_id: str,
    exp_id: str | None = None,
) -> str:
    """Run experiment: eval baseline + candidate on same dataset, compare results.
    Both use current live agent for now (version-based reconstruction is a future enhancement).
    Returns experiment ID.
    """
    if exp_id is None:
        exp_id = create_experiment(db_path, dataset_name, baseline_version_id, candidate_version_id)

    baseline_eval_id = await run_eval(dataset_name=dataset_name, db_path=db_path)
    candidate_eval_id = await run_eval(dataset_name=dataset_name, db_path=db_path)

    baseline_run = get_eval_run(db_path, baseline_eval_id)
    candidate_run = get_eval_run(db_path, candidate_eval_id)
    comparison = compare_eval_runs(baseline_run, candidate_run)

    baseline_cases = get_eval_case_results(db_path, baseline_eval_id)
    candidate_cases = get_eval_case_results(db_path, candidate_eval_id)
    case_diff = compare_cases(baseline_cases, candidate_cases)

    result = {**comparison, **case_diff}

    conn = _connect(db_path)
    with conn:
        conn.execute(
            """UPDATE experiments
               SET status = 'completed', completed_at = ?, baseline_eval_id = ?,
                   candidate_eval_id = ?, result = ?
               WHERE id = ?""",
            (datetime.now(timezone.utc).isoformat(), baseline_eval_id, candidate_eval_id,
             json.dumps(result), exp_id),
        )
    conn.close()
    return exp_id
