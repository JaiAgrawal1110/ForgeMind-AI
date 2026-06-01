// ============================================================
// TelemetryChart.jsx — Live line chart of telemetry over time
// Uses recharts library to render a real-time temperature graph
// Updates every 2 seconds as new WebSocket data arrives
// ============================================================

import React from "react";
import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from "recharts";

const TelemetryChart = ({ history, machineId }) => {
  // Format timestamp for X axis — show only time (HH:MM:SS)
  const formatTime = (timestamp) => {
    if (!timestamp) return "";
    return new Date(timestamp).toLocaleTimeString();
  };

  // Format data for recharts
  const chartData = history.map(reading => ({
    time: formatTime(reading.timestamp),
    temperature: reading.temperature,
    spindle: reading.spindle_speed / 100   // Scale down RPM to fit chart
  }));

  return (
    <div style={{
      background: "#1e1e2e",
      borderRadius: "12px",
      padding: "20px",
      marginTop: "20px"
    }}>
      <h3 style={{ color: "#e2e8f0", margin: "0 0 16px 0" }}>
        {machineId} — Live Telemetry
      </h3>

      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />

          <XAxis
            dataKey="time"
            stroke="#6b7280"
            tick={{ fill: "#6b7280", fontSize: 11 }}
            interval="preserveStartEnd"
          />

          <YAxis
            stroke="#6b7280"
            tick={{ fill: "#6b7280", fontSize: 11 }}
          />

          <Tooltip
            contentStyle={{ background: "#111827", border: "1px solid #374151" }}
            labelStyle={{ color: "#9ca3af" }}
            itemStyle={{ color: "#e2e8f0" }}
          />

          {/* Danger threshold line at 90°C */}
          <ReferenceLine
            y={90}
            stroke="#ef4444"
            strokeDasharray="4 4"
            label={{ value: "Danger 90°C", fill: "#ef4444", fontSize: 11 }}
          />

          {/* Temperature line */}
          <Line
            type="monotone"
            dataKey="temperature"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}                    // No dots — cleaner for live data
            name="Temp (°C)"
          />

          {/* Spindle speed line (scaled) */}
          <Line
            type="monotone"
            dataKey="spindle"
            stroke="#6366f1"
            strokeWidth={2}
            dot={false}
            name="Spindle (×100 RPM)"
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div style={{ display: "flex", gap: "20px", marginTop: "12px" }}>
        <LegendItem color="#10b981" label="Temperature (°C)" />
        <LegendItem color="#6366f1" label="Spindle (×100 RPM)" />
        <LegendItem color="#ef4444" label="Danger threshold" dashed />
      </div>
    </div>
  );
};

const LegendItem = ({ color, label, dashed }) => (
  <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
    <div style={{
      width: "20px", height: "2px",
      background: color,
      borderTop: dashed ? `2px dashed ${color}` : "none"
    }} />
    <span style={{ color: "#9ca3af", fontSize: "12px" }}>{label}</span>
  </div>
);

export default TelemetryChart;
