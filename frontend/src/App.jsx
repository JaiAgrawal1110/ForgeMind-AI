// ============================================================
// App.jsx — Root component, entry point of the React app
// Just renders the Dashboard for now
// Later: add routing for multiple pages (React Router)
// ============================================================

import React from "react";
import Dashboard from "./Dashboard";

// Global styles
const globalStyle = {
  margin: 0,
  padding: 0,
  background: "#0f0f1a",         // Dark background
  minHeight: "100vh",
  fontFamily: "'Inter', 'Segoe UI', sans-serif",
  color: "#e2e8f0"
};

// Pulse animation for anomaly badge (injected into head)
const style = document.createElement("style");
style.textContent = `
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: #0f0f1a; }
`;
document.head.appendChild(style);

function App() {
  return (
    <div style={globalStyle}>
      <Dashboard />
    </div>
  );
}

export default App;
