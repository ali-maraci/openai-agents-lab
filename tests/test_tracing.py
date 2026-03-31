from app.database import init_db, create_run
from app.tracing.store import save_span, get_spans_for_run
from app.tracing.collector import TraceCollector


def test_save_and_retrieve_spans(tmp_db_path):
    init_db(tmp_db_path)
    run_id = create_run(tmp_db_path, session_id="s1", input_text="test")

    save_span(tmp_db_path, {
        "run_id": run_id,
        "type": "agent_handoff",
        "name": "Triage Agent → Math Agent",
        "started_at": "2026-03-31T10:00:00Z",
        "completed_at": "2026-03-31T10:00:01Z",
        "duration_ms": 1000,
        "status": "ok",
    })
    save_span(tmp_db_path, {
        "run_id": run_id,
        "type": "tool_call",
        "name": "calculate",
        "started_at": "2026-03-31T10:00:01Z",
        "completed_at": "2026-03-31T10:00:02Z",
        "duration_ms": 500,
        "input_data": '{"expression": "2+3"}',
        "output_data": '"5"',
        "status": "ok",
    })

    spans = get_spans_for_run(tmp_db_path, run_id)
    assert len(spans) == 2
    assert spans[0]["type"] == "agent_handoff"
    assert spans[1]["type"] == "tool_call"
    assert spans[1]["name"] == "calculate"


def test_trace_collector_records_handoff():
    collector = TraceCollector(run_id="run_123")
    collector.record_handoff("Triage Agent", "Math Agent")
    assert len(collector.spans) == 1
    span = collector.spans[0]
    assert span["type"] == "agent_handoff"
    assert span["name"] == "Triage Agent → Math Agent"
    assert span["run_id"] == "run_123"


def test_trace_collector_records_tool_call():
    collector = TraceCollector(run_id="run_123")
    collector.record_tool_call("calculate", input_data='{"expression": "2+3"}', output_data='"5"')
    assert len(collector.spans) == 1
    span = collector.spans[0]
    assert span["type"] == "tool_call"
    assert span["name"] == "calculate"


def test_trace_collector_records_error():
    collector = TraceCollector(run_id="run_123")
    collector.record_error("input_guardrail", "Prompt injection detected")
    assert len(collector.spans) == 1
    span = collector.spans[0]
    assert span["type"] == "error"
    assert span["status"] == "error"
    assert span["error_message"] == "Prompt injection detected"


def test_trace_collector_flush(tmp_db_path):
    init_db(tmp_db_path)
    run_id = create_run(tmp_db_path, session_id="s1", input_text="test")
    collector = TraceCollector(run_id=run_id)
    collector.record_handoff("Triage Agent", "Math Agent")
    collector.record_tool_call("calculate")
    collector.flush(tmp_db_path)
    spans = get_spans_for_run(tmp_db_path, run_id)
    assert len(spans) == 2
