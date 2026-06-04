/**
 * PyBridge(tm) - Auto-generated RPC client with DevTools telemetry.
 */
export const server = new Proxy({}, {
  get(_, endpoint) {
    return async (payload = {}, file = null) => {
      window.__pyreact_rpc_logs = window.__pyreact_rpc_logs || [];
      const logEntry = {
        method: endpoint,
        args: payload,
        timestamp: new Date().toLocaleTimeString(),
        status: "pending"
      };
      window.__pyreact_rpc_logs.push(logEntry);
      window.dispatchEvent(new CustomEvent("pyreact-rpc-log-update"));

      if (window.__pyreact_wasm__) {
        try {
          const result = await window.runPythonWasm(endpoint, payload);
          logEntry.status = "success";
          logEntry.response = result;
          window.dispatchEvent(new CustomEvent("pyreact-rpc-log-update"));
          return result;
        } catch (err) {
          logEntry.status = "error";
          logEntry.response = err.message;
          window.dispatchEvent(new CustomEvent("pyreact-rpc-log-update"));
          throw err;
        }
      }

      try {
        const token = localStorage.getItem("pyreact_token");
        const headers = {};
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }
        let res;
        if (file) {
          const fd = new FormData();
          fd.append("file", file);
          Object.entries(payload).forEach(([k, v]) => fd.append(k, v));
          res = await fetch(`/api/${endpoint}`, { method: "POST", headers, body: fd });
        } else {
          headers["Content-Type"] = "application/json";
          res = await fetch(`/api/${endpoint}`, {
            method: "POST",
            headers,
            body: JSON.stringify(payload),
          });
        }
        const result = await res.json();
        logEntry.status = "success";
        logEntry.response = result;
        window.dispatchEvent(new CustomEvent("pyreact-rpc-log-update"));
        return result;
      } catch (err) {
        logEntry.status = "error";
        logEntry.response = err.message;
        window.dispatchEvent(new CustomEvent("pyreact-rpc-log-update"));
        throw err;
      }
    };
  },
});

// WebSocket Sync Client Manager
const wsCallbacks = new Set();
let ws = null;

function connectWS() {
  try {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host || "localhost:5000";
    ws = new WebSocket(`${protocol}//${host}/api/ws`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        for (const cb of wsCallbacks) {
          cb(data);
        }
      } catch (e) {}
    };
    ws.onclose = () => {
      setTimeout(connectWS, 3000);
    };
  } catch (e) {}
}

import { useEffect } from "react";
export const useSyncState = (topic, onUpdate) => {
  useEffect(() => {
    if (!ws) {
      connectWS();
    }
    const handler = (msg) => {
      if (msg.topic === topic) {
        onUpdate(msg.data);
      }
    };
    wsCallbacks.add(handler);
    return () => {
      wsCallbacks.delete(handler);
    };
  }, [topic, onUpdate]);

  const sendUpdate = (data) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ topic, data }));
    }
  };

  return sendUpdate;
};
