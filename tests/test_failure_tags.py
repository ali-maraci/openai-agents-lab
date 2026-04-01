from app.database import init_db, create_run, complete_run
from app.tracing.store import save_span
from app.monitoring.failure_tags import tag_run, get_tags_for_run, auto_tag_run, get_failure_summary


def test_tag_and_get(tmp_db_path):
    init_db(tmp_db_path)
    run_id = create_run(tmp_db_path, session_id="s1", input_text="test")
    tag_run(tmp_db_path, run_id, tag="timeout", source="auto")
    tags = get_tags_for_run(tmp_db_path, run_id)
    assert len(tags) == 1
    assert tags[0]["tag"] == "timeout"


def test_auto_tag_timeout(tmp_db_path):
    init_db(tmp_db_path)
    run_id = create_run(tmp_db_path, session_id="s1", input_text="test")
    import sqlite3
    conn = sqlite3.connect(tmp_db_path)
    conn.execute("UPDATE runs SET latency_ms = 35000, status = 'completed' WHERE id = ?", (run_id,))
    conn.commit()
    conn.close()
    auto_tag_run(tmp_db_path, run_id)
    tags = get_tags_for_run(tmp_db_path, run_id)
    tag_names = [t["tag"] for t in tags]
    assert "timeout" in tag_names


def test_auto_tag_looping(tmp_db_path):
    init_db(tmp_db_path)
    run_id = create_run(tmp_db_path, session_id="s1", input_text="test")
    complete_run(tmp_db_path, run_id, output="", status="completed")
    for i in range(5):
        save_span(tmp_db_path, {
            "run_id": run_id, "type": "tool_call", "name": "calculate",
            "started_at": f"2026-03-31T10:00:0{i}Z", "status": "ok",
        })
    auto_tag_run(tmp_db_path, run_id)
    tags = get_tags_for_run(tmp_db_path, run_id)
    tag_names = [t["tag"] for t in tags]
    assert "looping" in tag_names


def test_get_failure_summary(tmp_db_path):
    init_db(tmp_db_path)
    run_id = create_run(tmp_db_path, session_id="s1", input_text="test")
    tag_run(tmp_db_path, run_id, tag="timeout")
    tag_run(tmp_db_path, run_id, tag="bad_tool_choice")
    run_id2 = create_run(tmp_db_path, session_id="s2", input_text="test2")
    tag_run(tmp_db_path, run_id2, tag="timeout")
    summary = get_failure_summary(tmp_db_path)
    tags = {s["tag"]: s["count"] for s in summary}
    assert tags["timeout"] == 2
    assert tags["bad_tool_choice"] == 1
