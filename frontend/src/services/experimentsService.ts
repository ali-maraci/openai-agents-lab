const API_BASE = "http://127.0.0.1:8000/api";

export interface Version {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface ExperimentResult {
  id: string;
  dataset_name: string;
  baseline_version_id: string;
  candidate_version_id: string;
  status: string;
  result: {
    baseline_pass_rate: number;
    candidate_pass_rate: number;
    pass_rate_delta: number;
    regression: boolean;
    regressed: string[];
    fixed: string[];
    unchanged: string[];
  } | null;
}

export async function fetchVersions(): Promise<Version[]> {
  const res = await fetch(`${API_BASE}/versions`);
  const data = await res.json();
  return data.versions;
}

export async function createVersion(name: string, description?: string): Promise<Version> {
  const res = await fetch(`${API_BASE}/versions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });
  return res.json();
}

export async function startExperiment(
  dataset: string,
  baselineId: string,
  candidateId: string
): Promise<{ experiment_id: string }> {
  const res = await fetch(`${API_BASE}/experiments/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      dataset,
      baseline_version_id: baselineId,
      candidate_version_id: candidateId,
    }),
  });
  return res.json();
}

export async function fetchExperiment(expId: string): Promise<ExperimentResult> {
  const res = await fetch(`${API_BASE}/experiments/${expId}`);
  return res.json();
}

export async function fetchDatasets(): Promise<string[]> {
  const res = await fetch(`${API_BASE}/evals/datasets`);
  const data = await res.json();
  return data.datasets;
}
