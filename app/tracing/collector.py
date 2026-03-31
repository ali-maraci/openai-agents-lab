from datetime import datetime, timezone


class TraceCollector:
    """Collects trace spans during an agent run."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.spans: list[dict] = []

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def record_handoff(self, from_agent: str, to_agent: str):
        now = self._now_iso()
        self.spans.append({
            "run_id": self.run_id,
            "type": "agent_handoff",
            "name": f"{from_agent} → {to_agent}",
            "started_at": now,
            "completed_at": now,
            "duration_ms": 0,
            "status": "ok",
        })

    def record_tool_call(self, tool_name: str, input_data: str | None = None, output_data: str | None = None, duration_ms: int = 0):
        now = self._now_iso()
        self.spans.append({
            "run_id": self.run_id,
            "type": "tool_call",
            "name": tool_name,
            "started_at": now,
            "completed_at": now,
            "duration_ms": duration_ms,
            "input_data": input_data,
            "output_data": output_data,
            "status": "ok",
        })

    def record_error(self, name: str, error_message: str):
        now = self._now_iso()
        self.spans.append({
            "run_id": self.run_id,
            "type": "error",
            "name": name,
            "started_at": now,
            "completed_at": now,
            "duration_ms": 0,
            "status": "error",
            "error_message": error_message,
        })

    def flush(self, db_path: str):
        from app.tracing.store import save_span
        for span in self.spans:
            save_span(db_path, span)
