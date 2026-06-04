/**
 * PyReact Built-in UI Component Library v0.1
 * All components: React 18, Tailwind CSS, dark-mode first, accessible.
 */
import React, { useState } from "react";

export const UI = {
  Page: ({ children, className = "" }) => (
    <div className={`min-h-screen text-white p-6 ${className}`}
      style={{ backgroundColor: "var(--background, #0b0f19)", fontFamily: "var(--font, 'Inter', sans-serif)" }}>
      {children}
    </div>
  ),
  Navbar: ({ title = "App", children }) => (
    <nav className="fixed top-0 inset-x-0 z-50 backdrop-blur border-b border-white/10 px-6 py-3 flex items-center justify-between"
      style={{ backgroundColor: "rgba(17, 24, 39, 0.8)", borderBottomColor: "rgba(255, 255, 255, 0.1)" }}>
      <span className="font-bold text-lg text-white">{title}</span>
      <div className="flex gap-4">{children}</div>
    </nav>
  ),
  Sidebar: ({ children }) => (
    <aside className="w-64 min-h-screen border-r border-white/10 p-4 flex flex-col gap-2"
      style={{ backgroundColor: "var(--surface, #111827)", borderRightColor: "rgba(255, 255, 255, 0.1)" }}>
      {children}
    </aside>
  ),
  Dashboard: ({ children }) => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6 pt-20">{children}</div>
  ),
  Card: ({ title, children, className = "" }) => (
    <div className={`border border-white/10 p-6 shadow-xl ${className}`}
      style={{ backgroundColor: "var(--surface, #111827)", borderRadius: "var(--radius, 16px)", borderColor: "rgba(255, 255, 255, 0.1)" }}>
      {title && <h2 className="text-lg font-semibold mb-4 text-white">{title}</h2>}
      {children}
    </div>
  ),
  MetricCard: ({ label, value, trend }) => (
    <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-white/10 p-6"
      style={{ borderRadius: "var(--radius, 16px)", borderColor: "rgba(255, 255, 255, 0.1)" }}>
      <p className="text-sm text-gray-400 mb-1">{label}</p>
      <p className="text-3xl font-bold text-white">{value}</p>
      {trend && <p className="text-xs text-green-400 mt-1">{trend}</p>}
    </div>
  ),
  Button: ({ children, onClick, variant = "primary", loading = false, disabled = false }) => {
    const V = {
      primary: "text-white",
      secondary: "bg-gray-700 hover:bg-gray-600 text-white",
      danger: "bg-red-600 hover:bg-red-500 text-white",
      ghost: "bg-transparent hover:bg-white/10 text-white border border-white/20",
    };
    const s = {
      borderRadius: "var(--radius, 12px)",
    };
    if (variant === "primary") {
      s.backgroundColor = "var(--primary, #2563eb)";
    } else if (variant === "secondary") {
      s.backgroundColor = "var(--secondary, #4f46e5)";
    }
    return (
      <button onClick={onClick} disabled={disabled || loading} style={s}
        className={`inline-flex items-center gap-2 px-4 py-2 font-medium transition-all duration-150 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${V[variant] || V.primary}`}>
        {loading && <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />}
        {children}
      </button>
    );
  },
  Input: ({ label, value, onChange, placeholder = "", type = "text", helper }) => (
    <div className="flex flex-col gap-1">
      {label && <label className="text-sm font-medium text-gray-300">{label}</label>}
      <input type={type} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder}
        style={{ borderRadius: "var(--radius, 12px)" }}
        className="bg-gray-800 border border-white/10 px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition" />
      {helper && <p className="text-xs text-gray-500">{helper}</p>}
    </div>
  ),
  TextArea: ({ label, value, onChange, placeholder = "", rows = 4 }) => (
    <div className="flex flex-col gap-1">
      {label && <label className="text-sm font-medium text-gray-300">{label}</label>}
      <textarea value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} rows={rows}
        style={{ borderRadius: "var(--radius, 12px)" }}
        className="bg-gray-800 border border-white/10 px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition resize-none" />
    </div>
  ),
  Select: ({ label, value, onChange, options = [] }) => (
    <div className="flex flex-col gap-1">
      {label && <label className="text-sm font-medium text-gray-300">{label}</label>}
      <select value={value} onChange={e => onChange(e.target.value)}
        style={{ borderRadius: "var(--radius, 12px)" }}
        className="bg-gray-800 border border-white/10 px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  ),
  Table: ({ columns = [], rows = [] }) => (
    <div className="overflow-x-auto rounded-xl border border-white/10">
      <table className="w-full text-sm">
        <thead className="bg-gray-800/80">
          <tr>{columns.map(c => <th key={c} className="px-4 py-3 text-left text-gray-400 font-medium">{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-white/5 hover:bg-white/5 transition">
              {columns.map(c => <td key={c} className="px-4 py-3 text-gray-300">{row[c]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  ),
  Upload: ({ label = "Upload File", onFile, accept = "*" }) => (
    <label className="flex flex-col items-center justify-center gap-3 border-2 border-dashed border-white/20 rounded-2xl p-8 cursor-pointer hover:border-blue-500/50 hover:bg-blue-500/5 transition group">
      <svg className="w-10 h-10 text-gray-500 group-hover:text-blue-400 transition" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
      </svg>
      <span className="text-sm text-gray-400 group-hover:text-blue-300 transition">{label}</span>
      <input type="file" accept={accept} className="hidden" onChange={e => onFile && onFile(e.target.files[0])} />
    </label>
  ),
  Modal: ({ open, onClose, title, children }) => {
    if (!open) return null;
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
        <div className="relative bg-gray-900 border border-white/10 rounded-2xl p-6 shadow-2xl max-w-lg w-full mx-4 z-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">{title}</h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white transition" aria-label="Close">x</button>
          </div>
          {children}
        </div>
      </div>
    );
  },
  Alert: ({ type = "info", children }) => {
    const S = { info: "bg-blue-500/10 border-blue-500/30 text-blue-300", success: "bg-green-500/10 border-green-500/30 text-green-300", error: "bg-red-500/10 border-red-500/30 text-red-300", warning: "bg-yellow-500/10 border-yellow-500/30 text-yellow-300" };
    return <div className={`border rounded-xl px-4 py-3 text-sm ${S[type]}`}>{children}</div>;
  },
  Text: ({ children, size = "base", weight = "normal", color = "white", className = "" }) => (
    <p className={`text-${size} font-${weight} text-${color} ${className}`}>{children}</p>
  ),
  Heading: ({ children, level = 1 }) => {
    const Tag = `h${level}`;
    const sizes = { 1: "text-4xl font-bold", 2: "text-3xl font-bold", 3: "text-2xl font-semibold", 4: "text-xl font-semibold" };
    return <Tag className={`text-white ${sizes[level] || sizes[1]}`}>{children}</Tag>;
  },
  Divider: () => <hr className="border-white/10 my-4" />,
  Spinner: ({ size = "md" }) => {
    const s = { sm: "w-4 h-4", md: "w-6 h-6", lg: "w-10 h-10" };
    return <div className={`${s[size]} border-2 border-white/20 border-t-blue-500 rounded-full animate-spin`} />;
  },
  Badge: ({ children, color = "blue" }) => (
    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-${color}-500/20 text-${color}-300 border border-${color}-500/30`}>{children}</span>
  ),
  DataGrid: ({ data = [], columns = [] }) => <UI.Table columns={columns} rows={data} />,
  Chart: ({ type = "bar", data = [], height = 200 }) => {
    if (!data || data.length === 0) {
      return (
        <div className="flex items-center justify-center bg-gray-800/20 border border-white/5 rounded-xl text-gray-500 text-sm" style={{ height }}>
          No data available
        </div>
      );
    }
    const points = data.map((item, idx) => {
      if (typeof item === "number") return { label: String(idx + 1), value: item };
      if (typeof item === "object" && item !== null) {
        return {
          label: item.label || item.name || String(idx + 1),
          value: typeof item.value === "number" ? item.value : (typeof item.val === "number" ? item.val : 0)
        };
      }
      return { label: String(idx + 1), value: 0 };
    });
    const values = points.map(p => p.value);
    const maxVal = Math.max(...values, 1);
    const svgWidth = 500;
    const svgHeight = height - 40;
    if (type === "line") {
      const coords = points.map((p, idx) => {
        const x = (idx / (points.length - 1 || 1)) * (svgWidth - 40) + 20;
        const y = svgHeight - (p.value / maxVal) * (svgHeight - 20) - 10;
        return { x, y };
      });
      const linePath = coords.map((c, idx) => `${idx === 0 ? 'M' : 'L'} ${c.x} ${c.y}`).join(" ");
      const fillPath = coords.length > 0 
        ? `${linePath} L ${coords[coords.length - 1].x} ${svgHeight} L ${coords[0].x} ${svgHeight} Z`
        : "";
      return (
        <div className="bg-gray-900/50 border border-white/10 rounded-xl p-4 flex flex-col gap-2">
          <svg viewBox={`0 0 ${svgWidth} ${height}`} className="w-full h-auto">
            <defs>
              <linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--primary, #6366f1)" stopOpacity="0.4" />
                <stop offset="100%" stopColor="var(--primary, #6366f1)" stopOpacity="0.0" />
              </linearGradient>
            </defs>
            <line x1="20" y1={svgHeight} x2={svgWidth - 20} y2={svgHeight} stroke="rgba(255,255,255,0.05)" />
            <line x1="20" y1={svgHeight / 2} x2={svgWidth - 20} y2={svgHeight / 2} stroke="rgba(255,255,255,0.05)" />
            <line x1="20" y1="10" x2={svgWidth - 20} y2="10" stroke="rgba(255,255,255,0.05)" />
            {fillPath && <path d={fillPath} fill="url(#lineGrad)" />}
            {linePath && <path d={linePath} fill="none" stroke="var(--primary, #6366f1)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />}
            {coords.map((c, idx) => (
              <g key={idx} className="group cursor-pointer">
                <circle cx={c.x} cy={c.y} r="5" fill="var(--surface, #111827)" stroke="var(--primary, #6366f1)" strokeWidth="2" />
                <title>{points[idx].label}: {points[idx].value}</title>
              </g>
            ))}
            {coords.map((c, idx) => (
              <text key={idx} x={c.x} y={svgHeight + 20} fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">
                {points[idx].label}
              </text>
            ))}
          </svg>
        </div>
      );
    }
    const barWidth = (svgWidth - 40) / points.length - 10;
    return (
      <div className="bg-gray-900/50 border border-white/10 rounded-xl p-4 flex flex-col gap-2">
        <svg viewBox={`0 0 ${svgWidth} ${height}`} className="w-full h-auto">
          <defs>
            <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--primary, #6366f1)" />
              <stop offset="100%" stopColor="var(--secondary, #4f46e5)" />
            </linearGradient>
          </defs>
          <line x1="20" y1={svgHeight} x2={svgWidth - 20} y2={svgHeight} stroke="rgba(255,255,255,0.05)" />
          <line x1="20" y1={svgHeight / 2} x2={svgWidth - 20} y2={svgHeight / 2} stroke="rgba(255,255,255,0.05)" />
          <line x1="20" y1="10" x2={svgWidth - 20} y2="10" stroke="rgba(255,255,255,0.05)" />
          {points.map((p, idx) => {
            const x = idx * ((svgWidth - 40) / points.length) + 20 + 5;
            const barHeight = (p.value / maxVal) * (svgHeight - 20);
            const y = svgHeight - barHeight - 10;
            return (
              <g key={idx} className="group cursor-pointer">
                <rect x={x} y={y} width={barWidth} height={barHeight} fill="url(#barGrad)" rx="4" />
                <text x={x + barWidth / 2} y={svgHeight + 20} fill="rgba(255,255,255,0.4)" fontSize="10" textAnchor="middle">
                  {p.label}
                </text>
                <title>{p.label}: {p.value}</title>
              </g>
            );
          })}
        </svg>
      </div>
    );
  },
  Toast: ({ message, type = "info", visible }) => {
    if (!visible) return null;
    const S = { info: "bg-blue-600", success: "bg-green-600", error: "bg-red-600" };
    return <div className={`fixed bottom-6 right-6 z-50 px-5 py-3 rounded-xl text-white text-sm shadow-lg ${S[type]}`}>{message}</div>;
  },
  useAuth: () => {
    const [user, setUser] = useState(() => {
      const u = localStorage.getItem("pyreact_user");
      return u ? JSON.parse(u) : null;
    });
    const login = async (username, password) => {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (data.status === "ok" && data.token) {
        localStorage.setItem("pyreact_token", data.token);
        localStorage.setItem("pyreact_user", JSON.stringify(data.user));
        setUser(data.user);
        return { success: true };
      }
      return { success: false, message: data.message || "Login failed" };
    };
    const logout = () => {
      localStorage.removeItem("pyreact_token");
      localStorage.removeItem("pyreact_user");
      setUser(null);
    };
    return { user, login, logout, isAuthenticated: !!user };
  },
  Tabs: ({ tabs = [], activeTab, onChange }) => (
    <div className="flex border-b border-white/10 gap-2 mb-4">
      {tabs.map(t => (
        <button
          key={t}
          onClick={() => onChange(t)}
          className={`px-4 py-2 text-sm font-medium transition cursor-pointer border-b-2 ${
            activeTab === t ? "border-blue-500 text-blue-400" : "border-transparent text-gray-400 hover:text-white"
          }`}
        >
          {t}
        </button>
      ))}
    </div>
  ),
  Dropdown: ({ label = "Options", options = [], onSelect }) => {
    const [open, setOpen] = useState(false);
    return (
      <div className="relative inline-block text-left">
        <button onClick={() => setOpen(!open)} className="bg-gray-800 border border-white/10 px-4 py-2 rounded-xl text-white flex items-center gap-2 hover:bg-gray-700 transition">
          {label}
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
        </button>
        {open && (
          <>
            <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
            <div className="absolute right-0 mt-2 w-48 bg-gray-900 border border-white/10 rounded-xl shadow-xl z-20 overflow-hidden">
              {options.map(o => (
                <button
                  key={o.value || o}
                  onClick={() => { onSelect(o.value || o); setOpen(false); }}
                  className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-white/5 hover:text-white transition"
                >
                  {o.label || o}
                </button>
              ))}
            </div>
          </>
        )}
      </div>
    );
  },
  Accordion: ({ title, children }) => {
    const [open, setOpen] = useState(false);
    return (
      <div className="border border-white/10 rounded-xl overflow-hidden bg-gray-900/50 mb-3">
        <button onClick={() => setOpen(!open)} className="w-full px-5 py-4 flex items-center justify-between text-left font-medium text-white hover:bg-white/5 transition">
          <span>{title}</span>
          <svg className={`w-5 h-5 transition-transform ${open ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        {open && <div className="px-5 py-4 border-t border-white/10 text-gray-300 text-sm bg-gray-950/20">{children}</div>}
      </div>
    );
  },
  Calendar: ({ value, onChange }) => {
    const [date, setDate] = useState(value || new Date());
    const daysInMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
    const firstDayIndex = new Date(date.getFullYear(), date.getMonth(), 1).getDay();
    const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const handlePrev = () => setDate(new Date(date.getFullYear(), date.getMonth() - 1, 1));
    const handleNext = () => setDate(new Date(date.getFullYear(), date.getMonth() + 1, 1));
    const cells = [];
    for (let i = 0; i < firstDayIndex; i++) cells.push(null);
    for (let i = 1; i <= daysInMonth; i++) cells.push(new Date(date.getFullYear(), date.getMonth(), i));
    return (
      <div className="w-full max-w-sm bg-gray-900 border border-white/10 rounded-2xl p-4 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <button onClick={handlePrev} className="text-gray-400 hover:text-white transition">Prev</button>
          <span className="font-semibold text-white">{months[date.getMonth()]} {date.getFullYear()}</span>
          <button onClick={handleNext} className="text-gray-400 hover:text-white transition">Next</button>
        </div>
        <div className="grid grid-cols-7 gap-1 text-center text-xs font-semibold text-gray-400 mb-2">
          {["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"].map(d => <div key={d}>{d}</div>)}
        </div>
        <div className="grid grid-cols-7 gap-1">
          {cells.map((c, idx) => {
            if (!c) return <div key={idx} />;
            const isSelected = value && c.toDateString() === value.toDateString();
            return (
              <button
                key={idx}
                onClick={() => onChange && onChange(c)}
                className={`py-2 text-xs rounded-lg transition cursor-pointer font-medium ${
                  isSelected ? "bg-blue-600 text-white font-bold" : "text-gray-300 hover:bg-white/5"
                }`}
              >
                {c.getDate()}
              </button>
            );
          })}
        </div>
      </div>
    );
  },
  Chatbot: ({ endpoint, placeholder = "Ask agent..." }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const handleSend = async () => {
      if (!input.trim()) return;
      const userMsg = { role: "user", text: input };
      setMessages(prev => [...prev, userMsg]);
      setInput("");
      setLoading(true);
      try {
        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: input }),
        });
        const data = await res.json();
        setMessages(prev => [...prev, { role: "agent", text: data.response }]);
      } catch (err) {
        setMessages(prev => [...prev, { role: "agent", text: "[Error] Agent connection failed." }]);
      } finally {
        setLoading(false);
      }
    };
    return (
      <div className="border border-white/10 rounded-2xl overflow-hidden bg-gray-900 shadow-2xl flex flex-col h-[350px]">
        <div className="bg-gray-800/80 px-4 py-3 border-b border-white/10 text-white font-semibold text-sm flex items-center justify-between">
          <span>Agent Assistant Console</span>
          <span className="w-2.5 h-2.5 rounded-full bg-green-500 animate-pulse" />
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 text-xs py-10">Chat is empty. Start typing below.</div>
          )}
          {messages.map((m, idx) => (
            <div key={idx} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-2 text-xs leading-relaxed ${
                m.role === "user" ? "bg-blue-600 text-white rounded-br-none" : "bg-white/5 text-gray-300 border border-white/10 rounded-bl-none"
              }`}>
                {m.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white/5 border border-white/10 rounded-2xl rounded-bl-none px-4 py-2 text-xs text-gray-400 animate-pulse">
                Thinking...
              </div>
            </div>
          )}
        </div>
        <div className="p-3 border-t border-white/10 bg-gray-950/20 flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSend()}
            placeholder={placeholder}
            className="flex-1 bg-gray-800 border border-white/10 rounded-xl px-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <button onClick={handleSend} disabled={loading} className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-2 rounded-xl text-xs font-semibold cursor-pointer disabled:opacity-50 transition">
            Send
          </button>
        </div>
      </div>
    );
  },
};

export default UI;
