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


class EvalRunRequest(BaseModel):
    dataset: str


class EvalSummary(BaseModel):
    id: str
    dataset_name: str
    status: str
    total_cases: int
    passed: int
    failed: int
    pass_rate: float | None
    avg_latency_ms: float | None
    started_at: str
    completed_at: str | None


class CreateVersionRequest(BaseModel):
    name: str
    description: str | None = None
    snapshot_current: bool = True


class ExperimentRequest(BaseModel):
    dataset: str
    baseline_version_id: str
    candidate_version_id: str
