import { useEffect, useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Chip,
  Paper,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableContainer,
  CircularProgress,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import {
  Version,
  ExperimentResult,
  fetchVersions,
  createVersion,
  fetchDatasets,
  startExperiment,
  fetchExperiment,
} from "../services/experimentsService";

export default function ComparePage({ onBack }: { onBack: () => void }) {
  const [versions, setVersions] = useState<Version[]>([]);
  const [datasets, setDatasets] = useState<string[]>([]);
  const [newVersionName, setNewVersionName] = useState("");
  const [newVersionDesc, setNewVersionDesc] = useState("");
  const [baselineId, setBaselineId] = useState("");
  const [candidateId, setCandidateId] = useState("");
  const [dataset, setDataset] = useState("");
  const [experimentResult, setExperimentResult] = useState<ExperimentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [creatingVersion, setCreatingVersion] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchVersions().then(setVersions).catch(() => setError("Failed to load versions"));
    fetchDatasets().then(setDatasets).catch(() => setError("Failed to load datasets"));
  }, []);

  const handleCreateVersion = async () => {
    if (!newVersionName.trim()) return;
    setCreatingVersion(true);
    setError(null);
    try {
      await createVersion(newVersionName.trim(), newVersionDesc.trim() || undefined);
      setNewVersionName("");
      setNewVersionDesc("");
      const updated = await fetchVersions();
      setVersions(updated);
    } catch {
      setError("Failed to create version");
    } finally {
      setCreatingVersion(false);
    }
  };

  const handleRunExperiment = async () => {
    if (!baselineId || !candidateId || !dataset) return;
    if (baselineId === candidateId) {
      setError("Baseline and candidate versions must be different");
      return;
    }
    setLoading(true);
    setExperimentResult(null);
    setError(null);

    try {
      const { experiment_id } = await startExperiment(dataset, baselineId, candidateId);

      const poll = setInterval(async () => {
        try {
          const result = await fetchExperiment(experiment_id);
          if (result.status !== "running") {
            clearInterval(poll);
            setExperimentResult(result);
            setLoading(false);
          }
        } catch {
          clearInterval(poll);
          setError("Failed to fetch experiment results");
          setLoading(false);
        }
      }, 2000);
    } catch {
      setError("Failed to start experiment");
      setLoading(false);
    }
  };

  const getVersionName = (id: string) => versions.find((v) => v.id === id)?.name ?? id;

  const deltaColor = (delta: number) => (delta >= 0 ? "#2e7d32" : "#c62828");
  const deltaSign = (delta: number) => (delta >= 0 ? "+" : "");

  return (
    <Box sx={{ maxWidth: 900, mx: "auto", p: 3 }}>
      {/* Header */}
      <Box sx={{ display: "flex", alignItems: "center", mb: 3, gap: 1 }}>
        <IconButton onClick={onBack} size="small">
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h5" fontWeight={600}>
          Experiment Compare
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Version Management */}
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Snapshot Version
        </Typography>
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "flex-start" }}>
          <TextField
            label="Version name"
            size="small"
            value={newVersionName}
            onChange={(e) => setNewVersionName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleCreateVersion()}
            sx={{ minWidth: 200 }}
          />
          <TextField
            label="Description (optional)"
            size="small"
            value={newVersionDesc}
            onChange={(e) => setNewVersionDesc(e.target.value)}
            sx={{ minWidth: 260 }}
          />
          <Button
            variant="contained"
            onClick={handleCreateVersion}
            disabled={!newVersionName.trim() || creatingVersion}
            startIcon={creatingVersion ? <CircularProgress size={16} color="inherit" /> : undefined}
          >
            Snapshot Current
          </Button>
        </Box>

        {versions.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Existing versions ({versions.length})
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Created</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {versions.map((v) => (
                    <TableRow key={v.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500}>
                          {v.name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {v.description ?? "—"}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {new Date(v.created_at).toLocaleString()}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>

      {/* Experiment Form */}
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Run Experiment
        </Typography>
        <Box sx={{ display: "flex", gap: 2, flexWrap: "wrap", alignItems: "flex-end" }}>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Baseline version</InputLabel>
            <Select
              value={baselineId}
              label="Baseline version"
              onChange={(e) => setBaselineId(e.target.value)}
            >
              {versions.map((v) => (
                <MenuItem key={v.id} value={v.id}>
                  {v.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Candidate version</InputLabel>
            <Select
              value={candidateId}
              label="Candidate version"
              onChange={(e) => setCandidateId(e.target.value)}
            >
              {versions.map((v) => (
                <MenuItem key={v.id} value={v.id}>
                  {v.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Dataset</InputLabel>
            <Select
              value={dataset}
              label="Dataset"
              onChange={(e) => setDataset(e.target.value)}
            >
              {datasets.map((d) => (
                <MenuItem key={d} value={d}>
                  {d}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            color="secondary"
            onClick={handleRunExperiment}
            disabled={!baselineId || !candidateId || !dataset || loading}
            startIcon={loading ? <CircularProgress size={16} color="inherit" /> : undefined}
          >
            {loading ? "Running..." : "Run Experiment"}
          </Button>
        </Box>
      </Paper>

      {/* Results */}
      {experimentResult && experimentResult.result && (
        <Paper elevation={1} sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Results
          </Typography>

          {/* Summary alert */}
          {experimentResult.result.regression ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              Regression detected — candidate performed worse than baseline.
            </Alert>
          ) : experimentResult.result.pass_rate_delta > 0 ? (
            <Alert severity="success" sx={{ mb: 2 }}>
              Improvement — candidate outperformed baseline.
            </Alert>
          ) : (
            <Alert severity="info" sx={{ mb: 2 }}>
              No significant change between versions.
            </Alert>
          )}

          {/* Pass rate comparison */}
          <Box sx={{ display: "flex", gap: 4, mb: 3, flexWrap: "wrap" }}>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Baseline ({getVersionName(experimentResult.baseline_version_id)})
              </Typography>
              <Typography variant="h4" fontWeight={700}>
                {(experimentResult.result.baseline_pass_rate * 100).toFixed(1)}%
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Candidate ({getVersionName(experimentResult.candidate_version_id)})
              </Typography>
              <Typography variant="h4" fontWeight={700}>
                {(experimentResult.result.candidate_pass_rate * 100).toFixed(1)}%
              </Typography>
            </Box>
            <Box>
              <Typography variant="caption" color="text.secondary">
                Delta
              </Typography>
              <Typography
                variant="h4"
                fontWeight={700}
                sx={{ color: deltaColor(experimentResult.result.pass_rate_delta) }}
              >
                {deltaSign(experimentResult.result.pass_rate_delta)}
                {(experimentResult.result.pass_rate_delta * 100).toFixed(1)}%
              </Typography>
            </Box>
          </Box>

          {/* Regressed cases */}
          {experimentResult.result.regressed.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#c62828" }}>
                Regressed ({experimentResult.result.regressed.length})
              </Typography>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                {experimentResult.result.regressed.map((item) => (
                  <Chip key={item} label={item} size="small" color="error" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}

          {/* Fixed cases */}
          {experimentResult.result.fixed.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#2e7d32" }}>
                Fixed ({experimentResult.result.fixed.length})
              </Typography>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                {experimentResult.result.fixed.map((item) => (
                  <Chip key={item} label={item} size="small" color="success" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}

          {/* Unchanged cases */}
          {experimentResult.result.unchanged.length > 0 && (
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1 }} color="text.secondary">
                Unchanged ({experimentResult.result.unchanged.length})
              </Typography>
              <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
                {experimentResult.result.unchanged.map((item) => (
                  <Chip key={item} label={item} size="small" variant="outlined" />
                ))}
              </Box>
            </Box>
          )}
        </Paper>
      )}

      {/* Loading state when no result yet */}
      {loading && (
        <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 2 }}>
          <CircularProgress size={20} />
          <Typography color="text.secondary">Waiting for experiment to complete...</Typography>
        </Box>
      )}
    </Box>
  );
}
