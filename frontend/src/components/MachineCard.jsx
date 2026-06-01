// ============================================================
// MachineCard.jsx — Shows one machine's current status
// Displays: machine ID, status, live temperature, spindle speed
// Shows a red badge if machine is in anomaly state
// ============================================================

import React from "react";

const MachineCard = ({ machineId, data, connected }) => {
  // Determine if machine is in danger based on temperature
  const isAnomaly = data && data.temperature > 90;
  const isWarning = data && data.temperature > 80 && data.temperature <= 90;

  // Status color
  const statusColor = !connected
    ? "#6b7280"          // gray = disconnected
    : isAnomaly
    ? "#ef4444"          // red = danger
    : isWarning
    ? "#f59e0b"          // amber = warning
    : "#10b981";         // green = normal

  return (
    <div style={{
      background: "#1e1e2e",
      border: `2px solid ${statusColor}`,
      borderRadius: "12px",
      padding: "20px",
      minWidth: "280px",
      position: "relative"
    }}>
      {/* Anomaly badge — shows when temperature is critical */}
      {isAnomaly && (
        <div style={{
          position: "absolute",
          top: "12px",
          right: "12px",
          background: "#ef4444",
          color: "white",
          padding: "4px 10px",
          borderRadius: "20px",
          fontSize: "12px",
          fontWeight: "bold",
          animation: "pulse 1.5s infinite"         // Pulsing red badge
        }}>
          ⚠ ANOMALY
        </div>
      )}

      {/* Machine ID */}
      <h3 style={{ color: "#e2e8f0", margin: "0 0 8px 0", fontSize: "18px" }}>
        {machineId}
      </h3>

      {/* Connection status */}
      <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "16px" }}>
        <div style={{
          width: "8px", height: "8px",
          borderRadius: "50%",
          background: statusColor
        }} />
        <span style={{ color: "#9ca3af", fontSize: "13px" }}>
          {connected ? "Live" : "Disconnected"}
        </span>
      </div>

      {/* Telemetry readings */}
      {data ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          <Metric
            label="Temperature"
            value={`${data.temperature}°C`}
            danger={isAnomaly}
            warning={isWarning}
          />
          <Metric
            label="Spindle Speed"
            value={`${data.spindle_speed} RPM`}
          />
          <Metric
            label="State"
            value={data.machine_state}
          />
        </div>
      ) : (
        <p style={{ color: "#6b7280", fontSize: "14px" }}>Waiting for data...</p>
      )}
    </div>
  );
};

// Small component for each metric row
const Metric = ({ label, value, danger, warning }) => (
  <div style={{ display: "flex", justifyContent: "space-between" }}>
    <span style={{ color: "#9ca3af", fontSize: "14px" }}>{label}</span>
    <span style={{
      color: danger ? "#ef4444" : warning ? "#f59e0b" : "#e2e8f0",
      fontSize: "14px",
      fontWeight: "500"
    }}>
      {value}
    </span>
  </div>
);

export default MachineCard;
