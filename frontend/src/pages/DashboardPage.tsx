import { useEffect, useState } from "react";
import {
  Box, Typography, Paper, IconButton, Alert as MuiAlert, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from "@mui/material";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import {
  DashboardMetrics, Alert,
  fetchDashboardMetrics, fetchFailureSummary, fetchAlerts, resolveAlert,
} from "../services/dashboardService";

export default function DashboardPage({ onBack }: { onBack: () => void }) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [failures, setFailures] = useState<{ tag: string; count: number }[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    fetchDashboardMetrics().then(setMetrics);
    fetchFailureSummary().then(setFailures);
    fetchAlerts().then(setAlerts);
  }, []);

  const handleResolve = async (alertId: string) => {
    await resolveAlert(alertId);
    setAlerts(alerts.filter((a) => a.id !== alertId));
  };

  if (!metrics) {
    return (
      <Box sx={{ p: 3, maxWidth: 900, mx: "auto" }}>
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  const { run_stats, agent_distribution, latency_percentiles, runs_over_time } = metrics;

  return (
    <Box sx={{ p: 3, maxWidth: 900, mx: "auto" }}>
      {/* Header */}
      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mb: 3 }}>
        <IconButton onClick={onBack}><ArrowBackIcon /></IconButton>
        <Typography variant="h6">Dashboard</Typography>
      </Box>

      {/* Alerts */}
      {alerts.map((alert) => (
        <MuiAlert
          key={alert.id}
          severity={alert.severity === "critical" ? "error" : "warning"}
          action={<Button size="small" onClick={() => handleResolve(alert.id)}>Resolve</Button>}
          sx={{ mb: 1 }}
        >
          {alert.message}
        </MuiAlert>
      ))}

      {/* Stat Cards */}
      <Box sx={{ display: "flex", gap: 2, mb: 3, flexWrap: "wrap" }}>
        {[
          { label: "Total Runs", value: run_stats.total_runs },
          { label: "Completed", value: run_stats.completed, color: "#2cb6aa" },
          { label: "Failed", value: run_stats.failed, color: "#f44336" },
          { label: "Avg Latency", value: `${run_stats.avg_latency_ms}ms` },
        ].map((card) => (
          <Paper key={card.label} sx={{ p: 2, flex: "1 1 150px", textAlign: "center" }} variant="outlined">
            <Typography variant="caption" color="text.secondary">{card.label}</Typography>
            <Typography variant="h5" sx={{ color: card.color, fontWeight: 600 }}>{card.value}</Typography>
          </Paper>
        ))}
      </Box>

      {/* Runs Over Time Chart */}
      {runs_over_time.length > 0 && (
        <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Runs Over Time</Typography>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={runs_over_time}>
              <XAxis dataKey="day" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Line type="monotone" dataKey="completed" stroke="#2cb6aa" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="failed" stroke="#f44336" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      )}

      {/* Latency Percentiles */}
      <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>Latency Percentiles</Typography>
        <Box sx={{ display: "flex", gap: 3 }}>
          {(["p50", "p90", "p99"] as const).map((key) => (
            <Box key={key} sx={{ textAlign: "center" }}>
              <Typography variant="caption" color="text.secondary">{key.toUpperCase()}</Typography>
              <Typography variant="h6">{latency_percentiles[key]}ms</Typography>
            </Box>
          ))}
        </Box>
      </Paper>

      {/* Agent Distribution */}
      {agent_distribution.length > 0 && (
        <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>Agent Distribution</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow><TableCell>Agent</TableCell><TableCell align="right">Count</TableCell></TableRow>
              </TableHead>
              <TableBody>
                {agent_distribution.map((row) => (
                  <TableRow key={row.agent}>
                    <TableCell>{row.agent}</TableCell>
                    <TableCell align="right">{row.count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}

      {/* Failure Breakdown */}
      {failures.length > 0 && (
        <Paper variant="outlined" sx={{ p: 2 }}>
          <Typography variant="subtitle2" gutterBottom>Failure Breakdown</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow><TableCell>Tag</TableCell><TableCell align="right">Count</TableCell></TableRow>
              </TableHead>
              <TableBody>
                {failures.map((row) => (
                  <TableRow key={row.tag}>
                    <TableCell>{row.tag}</TableCell>
                    <TableCell align="right">{row.count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
}
