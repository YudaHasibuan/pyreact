import React, { useState, useEffect } from "react";
import { getSharedState } from "../store";

export default function DevTools() {
  const [open, setOpen] = useState(false);
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState("rpc");
  const [shared, setShared] = useState(null);

  useEffect(() => {
    const updateLogs = () => {
      setLogs([...(window.__pyreact_rpc_logs || [])]);
    };
    window.addEventListener("pyreact-rpc-log-update", updateLogs);
    updateLogs();
    
    const interval = setInterval(() => {
      try {
        const state = getSharedState();
        setShared(state);
      } catch (e) {}
    }, 1000);

    return () => {
      window.removeEventListener("pyreact-rpc-log-update", updateLogs);
      clearInterval(interval);
    };
  }, []);

  if (!open) {
    return (
      <div 
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-[9999] bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold text-xs px-4 py-2.5 rounded-full shadow-2xl cursor-pointer hover:scale-105 active:scale-95 transition-all duration-200 border border-white/10 flex items-center gap-1.5"
      >
        <span className="w-2.5 h-2.5 bg-green-400 rounded-full animate-ping" />
        PyReact DevTools
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-[450px] h-[500px] z-[9999] bg-[#0c101d]/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl flex flex-col overflow-hidden text-white font-sans text-left">
      {/* Header */}
      <div className="px-4 py-3 bg-white/5 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">PyReact DevTools</span>
          <span className="text-[10px] bg-white/10 text-white/60 px-2 py-0.5 rounded-full">v0.1.0</span>
        </div>
        <button 
          onClick={() => setOpen(false)}
          className="text-white/60 hover:text-white text-lg font-semibold hover:bg-white/10 w-6 h-6 rounded-full flex items-center justify-center transition"
        >
          &times;
        </button>
      </div>

      {/* Tabs */}
      <div className="flex bg-white/5 border-b border-white/5 text-xs">
        <button 
          onClick={() => setActiveTab("rpc")}
          className={`flex-1 py-2 font-medium border-b-2 transition ${activeTab === "rpc" ? "border-blue-500 text-blue-400 bg-white/5" : "border-transparent text-white/60 hover:text-white"}`}
        >
          RPC Log ({logs.length})
        </button>
        <button 
          onClick={() => setActiveTab("state")}
          className={`flex-1 py-2 font-medium border-b-2 transition ${activeTab === "state" ? "border-blue-500 text-blue-400 bg-white/5" : "border-transparent text-white/60 hover:text-white"}`}
        >
          Shared State
        </button>
        <button 
          onClick={() => setActiveTab("system")}
          className={`flex-1 py-2 font-medium border-b-2 transition ${activeTab === "system" ? "border-blue-500 text-blue-400 bg-white/5" : "border-transparent text-white/60 hover:text-white"}`}
        >
          System Info
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 p-4 overflow-y-auto text-sm">
        {activeTab === "rpc" && (
          <div className="space-y-3">
            {logs.length === 0 ? (
              <div className="text-center text-white/40 py-12">No RPC requests made yet.</div>
            ) : (
              logs.map((log, idx) => (
                <div key={idx} className="p-3 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="font-mono text-xs text-blue-400 font-bold">server.{log.method}()</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${log.status === "success" ? "bg-green-500/20 text-green-400" : log.status === "pending" ? "bg-yellow-500/20 text-yellow-400" : "bg-red-500/20 text-red-400"}`}>
                      {log.status}
                    </span>
                  </div>
                  <div className="text-xs text-white/60 font-mono space-y-1">
                    <div><span className="text-white/40">Args:</span> {JSON.stringify(log.args)}</div>
                    {log.response && <div><span className="text-white/40">Res:</span> {JSON.stringify(log.response)}</div>}
                    <div className="text-[10px] text-white/30 text-right">{log.timestamp}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "state" && (
          <div>
            {!shared ? (
              <div className="text-center text-white/40 py-12">No active global shared state.</div>
            ) : (
              <div className="font-mono text-xs space-y-2">
                <div className="text-white/40 mb-2">Live Store Variables:</div>
                {Object.entries(shared).map(([k, v]) => (
                  <div key={k} className="p-2.5 bg-white/5 rounded-lg border border-white/5 flex justify-between">
                    <span className="text-indigo-400 font-semibold">{k}</span>
                    <span className="text-green-400">{JSON.stringify(v)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "system" && (
          <div className="space-y-3 text-xs font-mono">
            <div className="p-3 bg-white/5 rounded-xl border border-white/5 space-y-2">
              <div className="flex justify-between"><span className="text-white/40">PyReact Version:</span><span>v0.1.0</span></div>
              <div className="flex justify-between"><span className="text-white/40">Environment:</span><span className="text-green-400 font-semibold">Development</span></div>
              <div className="flex justify-between"><span className="text-white/40">HMR Watcher:</span><span>Vite Hot Reload</span></div>
              <div className="flex justify-between"><span className="text-white/40">Database Engine:</span><span>SQLite ORM</span></div>
            </div>
            <div className="p-3 bg-white/5 rounded-xl border border-white/5">
              <div className="text-white/40 mb-2">Engine Architecture:</div>
              <div className="text-[11px] text-white/60 space-y-1 leading-relaxed">
                PyReact compiles single-file unified structures into isolated Python processes and static ESM React structures with automated RPC proxies.
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
