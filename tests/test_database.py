import sqlite3

import pytest

from app.database import init_db, create_run, complete_run, get_run, list_runs


def test_init_db_creates_tables(tmp_db_path):
    init_db(tmp_db_path)
    conn = sqlite3.connect(tmp_db_path)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    table_names = [t[0] for t in tables]
    assert "runs" in table_names
    assert "trace_spans" in table_names
    conn.close()


def test_create_and_get_run(tmp_db_path):
    init_db(tmp_db_path)
    run_id = create_run(tmp_db_path, session_id="sess_1", input_text="hello")
    run = get_run(tmp_db_path, run_id)
    assert run is not None
    assert run["id"] == run_id
    assert run["session_id"] == "sess_1"
    assert run["input"] == "hello"
    assert run["status"] == "running"


def test_complete_run(tmp_db_path):
    init_db(tmp_db_path)
    run_id = create_run(tmp_db_path, session_id="sess_1", input_text="hello")
    complete_run(tmp_db_path, run_id, output="world", status="completed", final_agent="General Agent", input_tokens=10, output_tokens=20)
    run = get_run(tmp_db_path, run_id)
    assert run["output"] == "world"
    assert run["status"] == "completed"
    assert run["final_agent"] == "General Agent"
    assert run["latency_ms"] is not None
    assert run["latency_ms"] >= 0


def test_list_runs(tmp_db_path):
    init_db(tmp_db_path)
    create_run(tmp_db_path, session_id="s1", input_text="first")
    create_run(tmp_db_path, session_id="s2", input_text="second")
    runs = list_runs(tmp_db_path)
    assert len(runs) == 2
    assert runs[0]["input"] == "second"  # most recent first


def test_list_runs_with_limit(tmp_db_path):
    init_db(tmp_db_path)
    for i in range(5):
        create_run(tmp_db_path, session_id=f"s{i}", input_text=f"msg{i}")
    runs = list_runs(tmp_db_path, limit=2)
    assert len(runs) == 2
