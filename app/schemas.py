from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str


class RunSummary(BaseModel):
    id: str
    session_id: str
    input: str
    output: str | None
    status: str
    final_agent: str | None
    started_at: str
    completed_at: str | None
    latency_ms: int | None
    input_tokens: int
    output_tokens: int


class RunDetail(RunSummary):
    spans: list[dict]
