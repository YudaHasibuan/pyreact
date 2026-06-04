# PyReact-Web 🚀

**The Python-Powered Fullstack Language** — v1.4.0

> Build beautiful AI-powered fullstack applications using a single language, a single file, and a single workflow.

**PyReact = Python Simplicity + React Power + AI Native Development**

---

## 📦 Installation & Quick Start

Installing PyReact is now simpler than ever. It is available on PyPI as `pyreact-web`:

```bash
# Install PyReact globally
pip install pyreact-web

# Create a new project
pyreact new myapp

# Start Flask + Vite dev servers
cd myapp
pyreact dev
```

---

## One File. Full Stack.

Here is a simple example showing PyBridge RPC, database schema definition, styles, routing, and PWA capabilities all defined in a single `.pyreact` file:

```pyreact
database {
    model Forecast {
        id = primary_key()
        value = integer()
        created_at = timestamp()
    }
}

server {
    def forecast(data):
        # Database ORM, RPC, and AI capabilities
        return {"result": [1, 4, 9, 16]}
}

pages {
    Home      = "/"
    Dashboard = "/dashboard" [guard]
    Login     = "/login"
}

component Dashboard():
    result, setResult = use_state(None)

    def runForecast():
        data = server.forecast([])
        setResult(data)

    return (
        <UI.Page>
            <UI.Navbar title="PyReact App" />
            <UI.NetworkStatus />
            <UI.Button onClick={runForecast}>Run Forecast</UI.Button>
            <UI.Chart type="line" data={result} />
        </UI.Page>
    )

style {
    primary = "#6366f1"
    radius  = "16px"
    background = "#0b0f19"
}
```

---

## ⚡ Key Features (Fase 15 - 23 Complete)

### 🩺 Self-Healing Compiler [Fase 15]
Auto-detects compiler syntax errors and resolves them iteratively using locally hosted LLMs (via Ollama) or remote AI fallbacks. Run compiler healing with:
```bash
pyreact compile app.pyreact --heal
```

### 🗺️ File-System & Declarative Routing [Fase 16]
Supports Next.js-style file-system routing (e.g. `pages/blog/[slug].pyreact`) and declarative `pages { ... }` routing blocks complete with authorization route guards.

### 🛡️ Type System & Validation [Fase 17]
Enforces type safety with Python type annotations and decorators like `@validate` to validate incoming requests and ORM mutations.

### 🔄 Real-time Synchronization [Fase 18]
Two-way server-client data synchronization utilizing WebSocket or Server-Sent Events (SSE) channels, with automated connection lifecycle management.

### 🧪 Integrated Testing Suite [Fase 19]
Perform component unit tests, API tests, and complete Playwright-driven end-to-end integration tests using a single testing module:
```bash
pyreact test
```

### 💻 VS Code Extension [Fase 20]
Complete developer tooling including syntax highlighting for `.pyreact` files, IntelliSense autocomplete, error diagnostics, and a live preview panel.

### ☁️ PyReact Cloud Deployment [Fase 21]
One-command production deployment to the PyReact Cloud cluster, including secrets management, domains, and a live web dashboard:
```bash
pyreact deploy
```

### 🌐 Hybrid Server-Side Rendering (SSR) [Fase 22]
Zero-dependency pre-rendering of client JSX directly in Python on Flask or FastAPI (no Node.js runtime required), coupled with client hydration via `ReactDOM.hydrateRoot`.

### 📴 Offline-First PWA & Background Sync [Fase 23]
- **Web App Manifest & SW**: Auto-generates `manifest.json` and a caching Service Worker (`sw.js`).
- **Offline RPC Queue**: Queues client calls to `server.*` when the device is offline and automatically replays them when connectivity is restored.
- **Local State Caching**: Persists your shared state automatically using LocalStorage.
- **UI Network Status Indicator**: Live status checking via the built-in `<UI.NetworkStatus />` component.

---

## 🗺️ Roadmap & Project Status

| Phase | Feature | Status |
|---|---|---|
| **1–14** | Lexer, Parser, AST, RPC, DB ORM, AI Agents, PPR Registry | ✅ Completed |
| **15** | Self-Healing Compiler (AI-powered) | ✅ Completed |
| **16** | File-System & Pages Routing | ✅ Completed |
| **17** | Type System & Request Validation | ✅ Completed |
| **18** | Real-Time Sync & WebSocket Client | ✅ Completed |
| **19** | E2E Testing Framework (Playwright) | ✅ Completed |
| **20** | VS Code Extension (Syntax, LSP, Live Preview) | ✅ Completed |
| **21** | One-Command Cloud Deploy & Dashboard | ✅ Completed |
| **22** | Hybrid Server-Side Rendering (SSR) | ✅ Completed |
| **23** | Offline-First PWA & Background Sync | ✅ Completed |
| **24** | Real-time Collaborative State & WebSockets | 🔲 Planned |
| **25** | GraphQL API Engine & Type-Safe Queries | 🔲 Planned |
| **26** | RBAC (Role-Based Access Control) & Guards | 🔲 Planned |

---

## 📄 License

MIT © Yuda Hasibuan
