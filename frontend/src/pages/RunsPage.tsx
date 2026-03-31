import { useEffect, useState } from "react";
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
  IconButton,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Run, RunDetail, Span, fetchRuns, fetchRunDetail } from "../services/runsService";

const statusColor: Record<string, "success" | "error" | "warning" | "info"> = {
  completed: "success",
  failed: "error",
  guardrail_blocked: "warning",
  running: "info",
};

function SpanTimeline({ spans }: { spans: Span[] }) {
  if (spans.length === 0) return <Typography variant="body2">No trace spans recorded.</Typography>;
  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="subtitle2" gutterBottom>Trace</Typography>
      {spans.map((span) => (
        <Box
          key={span.id}
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1,
            py: 0.5,
            pl: 1,
            borderLeft: `3px solid ${span.status === "error" ? "#f44336" : "#2cb6aa"}`,
            mb: 0.5,
          }}
        >
          <Chip label={span.type} size="small" variant="outlined" />
          <Typography variant="body2" sx={{ fontWeight: 500 }}>{span.name}</Typography>
          {span.duration_ms != null && (
            <Typography variant="caption" color="text.secondary">{span.duration_ms}ms</Typography>
          )}
          {span.error_message && (
            <Typography variant="caption" color="error">{span.error_message}</Typography>
          )}
        </Box>
      ))}
    </Box>
  );
}

export default function RunsPage({ onBack }: { onBack: () => void }) {
  const [runs, setRuns] = useState<Run[]>([]);
  const [selectedRun, setSelectedRun] = useState<RunDetail | null>(null);

  useEffect(() => {
    fetchRuns().then(setRuns);
  }, []);

  const handleRowClick = async (runId: string) => {
    const detail = await fetchRunDetail(runId);
    setSelectedRun(detail);
  };

  if (selectedRun) {
    return (
      <Box sx={{ p: 3, maxWidth: 900, mx: "auto" }}>
        <IconButton onClick={() => setSelectedRun(null)} sx={{ mb: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h6">Run {selectedRun.id.slice(0, 8)}...</Typography>
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2"><strong>Input:</strong> {selectedRun.input}</Typography>
          <Typography variant="body2"><strong>Output:</strong> {selectedRun.output || "—"}</Typography>
          <Typography variant="body2"><strong>Agent:</strong> {selectedRun.final_agent || "—"}</Typography>
          <Typography variant="body2"><strong>Status:</strong>{" "}
            <Chip label={selectedRun.status} size="small" color={statusColor[selectedRun.status] || "default"} />
          </Typography>
          <Typography variant="body2"><strong>Latency:</strong> {selectedRun.latency_ms ?? "—"}ms</Typography>
        </Box>
        <SpanTimeline spans={selectedRun.spans} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 900, mx: "auto" }}>
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 2 }}>
        <IconButton onClick={onBack}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h6">Runs</Typography>
      </Box>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Input</TableCell>
              <TableCell>Agent</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Latency</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {runs.map((run) => (
              <TableRow
                key={run.id}
                hover
                sx={{ cursor: "pointer" }}
                onClick={() => handleRowClick(run.id)}
              >
                <TableCell sx={{ whiteSpace: "nowrap" }}>
                  {new Date(run.started_at).toLocaleString()}
                </TableCell>
                <TableCell sx={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {run.input}
                </TableCell>
                <TableCell>{run.final_agent || "—"}</TableCell>
                <TableCell>
                  <Chip label={run.status} size="small" color={statusColor[run.status] || "default"} />
                </TableCell>
                <TableCell>{run.latency_ms ?? "—"}ms</TableCell>
              </TableRow>
            ))}
            {runs.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center">No runs yet. Send a chat message first.</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
