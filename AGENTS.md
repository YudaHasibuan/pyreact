# AGENTS.md — PyReact Language Reference for AI Assistants

> This file teaches AI coding assistants (Cursor, Copilot, Claude, etc.) how to write correct PyReact code.
> ALWAYS follow these rules when generating or editing `.pyreact` files.

## What is PyReact?

PyReact is a Python-powered fullstack language. A single `.pyreact` file compiles into:
- **Backend**: Python Flask API server (auto-generated routes)
- **Frontend**: React 18 + Vite + Tailwind CSS (auto-generated components)
- **Bridge**: PyBridge RPC connects frontend `server.funcName()` calls to backend Flask endpoints

## Critical Rules

1. **NEVER write raw React JSX files** — always write `.pyreact` syntax
2. **NEVER write raw Flask/Python server files** — use `server { }` blocks
3. **NEVER write raw HTML/CSS files** — use `component` + `style { }` blocks
4. **NEVER use `import React` or `from react`** inside `.pyreact` files — it's auto-generated
5. **NEVER use `fetch()` or `axios`** — use `server.funcName()` for all API calls
6. **NEVER use `useState` or `useEffect`** (camelCase) — use `use_state` and `use_effect` (snake_case)

## Syntax Reference

### File Structure

A `.pyreact` file contains one or more of these top-level blocks:

```
server { }          # Backend Python functions (REQUIRED — brace syntax)
component Name():   # UI component (REQUIRED — indent syntax)
style { }           # Design tokens (optional — brace syntax)
pages { }           # Routing (optional — brace syntax)
shared_state { }    # Global reactive state (optional — brace syntax)
database { }        # ORM config (optional — brace syntax)
dependencies { }    # pip/npm packages (optional — brace syntax)
realtime { }        # WebSocket config (optional — brace syntax)
graphql { }         # GraphQL schema (optional — brace syntax)
rbac { }            # Role-based access control (optional — brace syntax)
webrtc { }          # P2P audio/video (optional — brace syntax)
middleware { }       # Request interceptors (optional — brace syntax)
```

### Syntax Convention

- **Brace syntax** `{ }` — used for config/data blocks: `server`, `style`, `pages`, `shared_state`, `database`, `dependencies`, `realtime`, `graphql`, `rbac`, `webrtc`, `middleware`
- **Indent syntax** `():` — used for `component` blocks (more Pythonic)

## Block Reference with Examples

### 1. `server { }` — Backend API Functions

Defines Python functions that become Flask API endpoints. Each `def` becomes a `POST /api/function_name` route.

```python
server {
    def get_users():
        users = [{"id": 1, "name": "Alice", "role": "admin"}]
        return {"users": users}

    def create_user(name: str, email: str):
        return {"id": 2, "name": name, "email": email}
}
```

### 2. `component Name():` — UI Components

```python
component UserProfile():
    name, setName = use_state("")
    loading, setLoading = use_state(False)
    user, setUser = use_state(None)

    def loadUser():
        setLoading(True)
        data = server.get_user(name)
        setUser(data)
        setLoading(False)

    return (
        <UI.Page>
            <UI.Navbar title="User Profile" />
            <div className="pt-24 max-w-xl mx-auto px-4">
                <UI.Card title="User Info">
                    <UI.Input label="Name" value={name} onChange={setName} />
                    <UI.Button onClick={loadUser} loading={loading}>Load</UI.Button>
                </UI.Card>
            </div>
        </UI.Page>
    )
```

**Rules:**
- Component names MUST start with uppercase (PascalCase)
- State: `value, setValue = use_state(initial)` compiles to React useState
- Handlers: `def handlerName():` compiles to async arrow function
- Always call backend via `server.functionName(args)` — NEVER fetch()
- Use `<UI.ComponentName>` for built-in components
- Use `className=` (not `class=`) for CSS classes (Tailwind CSS)

### 3. `style { }` — Design Tokens

```python
style {
    primary    = "#2563eb"
    secondary  = "#7c3aed"
    background = "#030712"
    radius     = "16px"
    font       = "Inter"
}
```

### 4. `pages { }` — File-System Routing

```python
pages {
    Home      = "/"
    About     = "/about"
    Dashboard = "/dashboard" [guard]
    Login     = "/login"
}
```

### 5. `shared_state { }` — Global Reactive State

```python
shared_state {
    current_user = None
    theme = "dark"
}
```

Access in components via `shared.variableName`.

### 6. `database { }` — ORM Configuration

```python
database {
    provider = "sqlite"
    url = "db.sqlite"
}
```

### 7. `dependencies { }` — Package Declarations

```python
dependencies {
    pip = ["flask-cors", "pillow"]
    npm = ["lodash", "date-fns"]
}
```

### 8. `middleware { }` — Request Interceptors

```python
middleware {
    def auth_guard(request):
        token = request.headers.get("Authorization")
        if not token:
            return {"status": 401, "message": "Unauthorized"}
}
```

## UI Components Reference

All built-in components are accessed via `<UI.ComponentName>`:

**Layout:** Page, Navbar, Sidebar, Dashboard
**Data Display:** Card, MetricCard, Table, DataGrid, Badge, Text, Heading, Divider
**Forms:** Button (variant: primary|secondary|danger|ghost), Input, TextArea, Select, Upload
**Feedback:** Alert (type: info|success|error|warning), Toast, Spinner, Modal
**Navigation:** Tabs, Dropdown, Accordion
**Advanced:** Chart (type: bar|line), Calendar, Chatbot, NetworkStatus, useAuth

## Hooks Reference

| PyReact Hook | Description |
|-------------|-------------|
| `value, setValue = use_state(initial)` | Local component state |
| `use_effect(def(): ..., [deps])` | Side effects |
| `doc, update, live = useRealtimeChannel(topic, id)` | Real-time sync |
| `const { user, login, logout, isAuthenticated } = UI.useAuth()` | Authentication |

## CLI Commands

```bash
pyreact new <name>                    # Create new project
pyreact dev                           # Start dev servers
pyreact build                         # Production build
pyreact compile [file]                # Compile without build
pyreact doctor                        # Diagnose environment
pyreact generate component <Name>     # Scaffold a component
pyreact deploy --platform <name>      # Generate vercel|fly|railway|render|digitalocean config
pyreact db [migrate|status|rollback]  # Manage database migrations
pyreact env check                     # Validate project environment variables
```

## File Header Convention

Every PyReact file can optional start with a metadata header structure to declare its purpose and components:
```python
# @pyreact app
# @name: My App Name
# @description: Short description of this app
# @version: 1.0.0
# @blocks: server, component, style
```

## Developer Quick Reference (Flask & React Mapping)

### Flask -> PyReact Mental Model

| Flask / Python Backend | PyReact equivalent |
|---|---|
| `app.py` | `app.pyreact` (unified entry file) |
| `@app.route('/api/x', methods=['POST'])` | `def x():` defined inside `server { }` block |
| `request.json['name']` / `request.form['name']` | Function parameter: `def create(name: str):` (type hinted) |
| `jsonify({"status": "ok"})` | `return {"status": "ok"}` |
| `SQLAlchemy model` | `class DbModel(db.Model):` inside `server { }` block |
| `Flask Blueprint` | Component files in `components/` |
| `@login_required` | `[guard]` flag on page configuration in `pages { }` |
| `CORS(app)` | Auto-configured by PyReact compiler |

### React -> PyReact Mental Model

| React / JS Frontend | PyReact equivalent |
|---|---|
| `useState(initial)` | `val, setVal = use_state(initial)` |
| `useEffect(() => {}, [])` | `use_effect(def(): ..., [])` |
| `fetch('/api/x')` / `axios` | `server.x()` (PyBridge RPC) |
| `export default function App()` | `component App():` (indent syntax) |
| `import { useState }` | (auto-imported, do not write imports) |
| `<div onClick={() => fn()}>` | `<div onClick={fn}>` (pythonic reference) |
| `BrowserRouter` / `Routes` | `pages { }` block configuration |
| Zustand / Redux / Context | `shared_state { }` global reactive state |
| `tailwind.config.js` | `style { }` block design tokens |

## Decision Tree for AI Coding

To build a feature, follow this tree:
1. **Need database operations?** -> Define model inside `server { }` block. Ensure `database { }` config is present.
2. **Need API / backend functions?** -> Define a python function inside the `server { }` block.
3. **Need local state?** -> Use `val, setVal = use_state(initial)`.
4. **Need global state shared across pages?** -> Define in `shared_state { }` block and access via `shared.varName`.
5. **Need page routing?** -> Define pages in the `pages { }` block (or create `.pyreact` files in a `pages/` directory).
6. **Need real-time updates?** -> Declare channels in `realtime { }` and use `useRealtimeChannel(topic, id)`.

## Things to Avoid

| Don't | Do Instead |
|-------|-----------|
| `const [x, setX] = useState(0)` | `x, setX = use_state(0)` |
| `useEffect(() => {}, [])` | `use_effect(def(): ..., [])` |
| `fetch("/api/endpoint")` | `server.endpoint(args)` |
| `import React from "react"` | (auto-imported) |
| `export default function X()` | `component X():` |
| JavaScript `===` | Python `==` |
| JavaScript `!==` | Python `!=` |
| `null` (in handlers/state) | `None` |
| `true` / `false` | `True` / `False` |
