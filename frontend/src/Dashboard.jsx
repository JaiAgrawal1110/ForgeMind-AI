// ============================================================
// Dashboard.jsx — Main dashboard page
// Shows all machines, their live telemetry, and active alerts
// Each machine has its own WebSocket connection
// ============================================================

import React, { useState } from "react";
import MachineCard from "./components/MachineCard";
import TelemetryChart from "./components/TelemetryChart";
import AlertPanel from "./components/AlertPanel";
import useWebSocket from "./hooks/useWebSocket";

// Individual machine panel — card + chart together
const MachinPanel = ({ machineId }) => {
  const { data, history, connected } = useWebSocket(machineId);

  return (
    <div style={{ marginBottom: "30px" }}>
      <MachineCard machineId={machineId} data={data} connected={connected} />
      <TelemetryChart history={history} machineId={machineId} />
    </div>
  );
};

const Dashboard = () => {
  // The machines we're monitoring — add more as you create them
  const machines = ["CNC-001", "CNC-002", "CNC-003"];

  return (
    <div style={{ padding: "30px" }}>
      <h1 style={{ color: "#e2e8f0", marginBottom: "8px" }}>
        Industrial AI Platform
      </h1>
      <p style={{ color: "#6b7280", marginBottom: "30px" }}>
        Real-time machine monitoring — {machines.length} machines active
      </p>

      {/* Machine panels side by side */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
        gap: "20px"
      }}>
        {machines.map(id => (
          <MachinPanel key={id} machineId={id} />
        ))}
      </div>

      {/* Alert panel below */}
      <AlertPanel />
    </div>
  );
};

export default Dashboard;
