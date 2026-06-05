// ============================================================
// useWebSocket.js — Custom React hook for WebSocket connection
// A "hook" is a reusable piece of logic in React
// This one manages the WebSocket connection to our backend
// and gives any component access to live telemetry data
// ============================================================

import { useState, useEffect, useRef } from "react";

const useWebSocket = (machineId) => {
  const [data, setData] = useState(null);         // Latest telemetry reading
  const [history, setHistory] = useState([]);     // Last 30 readings for chart
  const [connected, setConnected] = useState(false);
  const ws = useRef(null);                         // WebSocket reference

  useEffect(() => {
    if (!machineId) return;

    // Connect to our FastAPI WebSocket endpoint
    const url = `ws://15.134.229.0:8000/ws/telemetry/${machineId}`;
    ws.current = new WebSocket(url);

    // When connection opens
    ws.current.onopen = () => {
      console.log(`WebSocket connected: ${machineId}`);
      setConnected(true);
    };

    // When we receive a message from the server
    ws.current.onmessage = (event) => {
      const reading = JSON.parse(event.data);
      setData(reading);                            // Update latest reading

      // Keep last 30 readings for the chart
      setHistory(prev => {
        const updated = [...prev, reading];
        return updated.slice(-30);                 // Only keep last 30
      });
    };

    // When connection closes
    ws.current.onclose = () => {
      console.log(`WebSocket disconnected: ${machineId}`);
      setConnected(false);
    };

    // Cleanup: close WS when component unmounts
    return () => {
      ws.current?.close();
    };
  }, [machineId]);   // Re-run if machineId changes

  return { data, history, connected };
};

export default useWebSocket;
