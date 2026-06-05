// ============================================================
// AlertPanel.jsx — Shows active alerts from the backend
// Polls GET /alerts?resolved=false every 10 seconds
// Shows severity, machine ID, message, and resolve button
// ============================================================

import React, { useState, useEffect } from "react";
import axios from "axios";

const AlertPanel = () => {
  const [alerts, setAlerts] = useState([]);

  // Fetch unresolved alerts every 10 seconds
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await axios.get("http://15.134.229.0:8000/alerts?resolved=false");
        setAlerts(res.data);
      } catch (err) {
        console.error("Failed to fetch alerts:", err);
      }
    };

    fetchAlerts();                              // Fetch immediately on mount
    const interval = setInterval(fetchAlerts, 10000);  // Then every 10s
    return () => clearInterval(interval);       // Cleanup on unmount
  }, []);

  // Resolve an alert
  const resolveAlert = async (alertId) => {
    try {
      await axios.put(`http://15.134.229.0:8000/alerts/${alertId}/resolve`);
      setAlerts(prev => prev.filter(a => a.id !== alertId));  // Remove from UI
    } catch (err) {
      console.error("Failed to resolve alert:", err);
    }
  };

  // Severity colors
  const severityColor = {
    low: "#6b7280",
    medium: "#f59e0b",
    high: "#f97316",
    critical: "#ef4444"
  };

  return (
    <div style={{
      background: "#1e1e2e",
      borderRadius: "12px",
      padding: "20px",
      marginTop: "20px"
    }}>
      <h3 style={{ color: "#e2e8f0", margin: "0 0 16px 0" }}>
        Active Alerts
        {alerts.length > 0 && (
          <span style={{
            marginLeft: "10px",
            background: "#ef4444",
            color: "white",
            borderRadius: "50%",
            padding: "2px 8px",
            fontSize: "13px"
          }}>
            {alerts.length}
          </span>
        )}
      </h3>

      {alerts.length === 0 ? (
        <p style={{ color: "#6b7280", fontSize: "14px" }}>No active alerts ✓</p>
      ) : (
        alerts.map(alert => (
          <div key={alert.id} style={{
            border: `1px solid ${severityColor[alert.severity]}`,
            borderRadius: "8px",
            padding: "12px",
            marginBottom: "10px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div>
              {/* Severity badge */}
              <span style={{
                background: severityColor[alert.severity],
                color: "white",
                padding: "2px 8px",
                borderRadius: "4px",
                fontSize: "11px",
                fontWeight: "bold",
                textTransform: "uppercase",
                marginRight: "8px"
              }}>
                {alert.severity}
              </span>
              <span style={{ color: "#9ca3af", fontSize: "12px" }}>
                {alert.machine_id}
              </span>
              <p style={{ color: "#e2e8f0", margin: "6px 0 0 0", fontSize: "14px" }}>
                {alert.message}
              </p>
            </div>

            {/* Resolve button */}
            <button
              onClick={() => resolveAlert(alert.id)}
              style={{
                background: "transparent",
                border: "1px solid #374151",
                color: "#9ca3af",
                padding: "6px 12px",
                borderRadius: "6px",
                cursor: "pointer",
                fontSize: "12px",
                whiteSpace: "nowrap"
              }}
            >
              Resolve
            </button>
          </div>
        ))
      )}
    </div>
  );
};

export default AlertPanel;
