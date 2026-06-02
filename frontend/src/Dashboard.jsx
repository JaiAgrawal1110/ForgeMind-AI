// ============================================================
// Dashboard.jsx — Main dashboard page
// Fetches machines dynamically from MongoDB via GET /machines
// Each machine gets its own WebSocket connection for live data
// ============================================================

import React, { useState, useEffect } from "react";
import axios from "axios";
import MachineCard from "./components/MachineCard";
import TelemetryChart from "./components/TelemetryChart";
import AlertPanel from "./components/AlertPanel";
import useWebSocket from "./hooks/useWebSocket";

const API = "http://localhost:8000";

// Individual machine panel — card + chart together
const MachinePanel = ({ machineId }) => {
  const { data, history, connected } = useWebSocket(machineId);

  return (
    <div style={{ marginBottom: "30px" }}>
      <MachineCard machineId={machineId} data={data} connected={connected} />
      <TelemetryChart history={history} machineId={machineId} />
    </div>
  );
};

const Dashboard = () => {
  const [machines, setMachines] = useState([]);   // Fetched from MongoDB
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch machines from MongoDB on load
  useEffect(() => {
    const fetchMachines = async () => {
      try {
        const res = await axios.get(`${API}/machines`);
        // Extract just the machine_ids for WebSocket connections
        setMachines(res.data.map(m => m.machine_id));
        setLoading(false);
      } catch (err) {
        setError("Failed to fetch machines from backend");
        setLoading(false);
      }
    };

    fetchMachines();

    // Refresh machine list every 30 seconds in case new machines are added
    const interval = setInterval(fetchMachines, 5000);
      return () => clearInterval(interval);
  }, []);

  if (loading) return (
    <div style={{ padding: "30px", color: "#9ca3af" }}>
      Loading machines from database...
    </div>
  );

  if (error) return (
    <div style={{ padding: "30px", color: "#ef4444" }}>
      {error} — is the backend running?
    </div>
  );

  return (
    <div style={{ padding: "30px" }}>
      <h1 style={{ color: "#e2e8f0", marginBottom: "8px" }}>
        Industrial AI Platform
      </h1>
      <p style={{ color: "#6b7280", marginBottom: "30px" }}>
        Real-time machine monitoring — {machines.length} machines active
      </p>

      {machines.length === 0 ? (
        <p style={{ color: "#6b7280" }}>
          No machines found. Add one via POST /machines in the API.
        </p>
      ) : (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))",
          gap: "20px"
        }}>
          {machines.map(id => (
            <MachinePanel key={id} machineId={id} />
          ))}
        </div>
      )}

      <AlertPanel />
    </div>
  );
};

export default Dashboard;
