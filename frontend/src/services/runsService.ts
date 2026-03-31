const API_BASE = "http://127.0.0.1:8000/api";

export interface Run {
  id: string;
  session_id: string;
  input: string;
  output: string | null;
  status: string;
  final_agent: string | null;
  started_at: string;
  completed_at: string | null;
  latency_ms: number | null;
  input_tokens: number;
  output_tokens: number;
}

export interface Span {
  id: string;
  run_id: string;
  type: string;
  name: string;
  started_at: string;
  completed_at: string | null;
  duration_ms: number | null;
  input_data: string | null;
  output_data: string | null;
  status: string;
  error_message: string | null;
}

export interface RunDetail extends Run {
  spans: Span[];
}

export async function fetchRuns(limit = 50): Promise<Run[]> {
  const res = await fetch(`${API_BASE}/runs?limit=${limit}`);
  const data = await res.json();
  return data.runs;
}

export async function fetchRunDetail(runId: string): Promise<RunDetail> {
  const res = await fetch(`${API_BASE}/runs/${runId}`);
  return res.json();
}
