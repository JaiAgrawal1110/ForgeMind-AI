// ============================================================
// index.js — Mounts the React app into the HTML page
// This is the actual entry point — React starts here
// ============================================================

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
