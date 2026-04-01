const API_BASE = "http://127.0.0.1:8000/api";

export interface RunStats {
  total_runs: number;
  completed: number;
  failed: number;
  guardrail_blocked: number;
  avg_latency_ms: number;
  total_input_tokens: number;
  total_output_tokens: number;
}

export interface DashboardMetrics {
  run_stats: RunStats;
  agent_distribution: { agent: string; count: number }[];
  status_distribution: { status: string; count: number }[];
  latency_percentiles: { p50: number; p90: number; p99: number };
  runs_over_time: { day: string; total: number; completed: number; failed: number }[];
}

export interface Alert {
  id: string;
  type: string;
  severity: string;
  message: string;
  created_at: string;
}

export async function fetchDashboardMetrics(days = 7): Promise<DashboardMetrics> {
  const res = await fetch(`${API_BASE}/dashboard/metrics?days=${days}`);
  return res.json();
}

export async function fetchFailureSummary(): Promise<{ tag: string; count: number }[]> {
  const res = await fetch(`${API_BASE}/dashboard/failures`);
  const data = await res.json();
  return data.failure_summary;
}

export async function fetchAlerts(): Promise<Alert[]> {
  const res = await fetch(`${API_BASE}/dashboard/alerts`);
  const data = await res.json();
  return data.alerts;
}

export async function resolveAlert(alertId: string): Promise<void> {
  await fetch(`${API_BASE}/dashboard/alerts/${alertId}/resolve`, { method: "POST" });
}
