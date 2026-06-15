"""PYREACT Language Server Protocol (LSP) Server.
Handles auto-completions, hover documentation, blocks detection, cross-boundary definition jump, and real-time validation.
"""

# ── Hover documentation data ────────────────────────────────────────────────────
_UI_COMPONENT_DOCS = {
    "Page": ("<UI.Page>", "Root page container with dark background.", "Props: className=str"),
    "Navbar": ("<UI.Navbar>", "Fixed top navigation bar.", "Props: title=str, children"),
    "Sidebar": ("<UI.Sidebar>", "Side navigation panel.", "Props: children"),
    "Dashboard": ("<UI.Dashboard>", "Responsive grid layout for cards.", "Props: children"),
    "Card": ("<UI.Card>", "Content card with optional title.", "Props: title=str, className=str, children"),
    "MetricCard": ("<UI.MetricCard>", "KPI display card with label/value/trend.", "Props: label=str, value=any, trend=str"),
    "Button": ("<UI.Button>", "Action button with variants.", "Props: onClick=fn, variant=primary|secondary|danger|ghost, loading=bool, disabled=bool, children"),
    "Input": ("<UI.Input>", "Text input field with label.", "Props: label=str, value=str, onChange=fn, placeholder=str, type=str, helper=str"),
    "TextArea": ("<UI.TextArea>", "Multi-line text input.", "Props: label=str, value=str, onChange=fn, placeholder=str, rows=int"),
    "Select": ("<UI.Select>", "Dropdown select input.", "Props: label=str, value=str, onChange=fn, options=list"),
    "Table": ("<UI.Table>", "Data table with columns and rows.", "Props: columns=list, rows=list"),
    "Upload": ("<UI.Upload>", "File upload drop zone.", "Props: label=str, onFile=fn, accept=str"),
    "Modal": ("<UI.Modal>", "Overlay dialog modal.", "Props: open=bool, onClose=fn, title=str, children"),
    "Alert": ("<UI.Alert>", "Inline alert/notification banner.", "Props: type=info|success|error|warning, children"),
    "Text": ("<UI.Text>", "Text paragraph component.", "Props: size=str, weight=str, color=str, className=str, children"),
    "Heading": ("<UI.Heading>", "Section heading h1-h4.", "Props: level=1|2|3|4, children"),
    "Divider": ("<UI.Divider>", "Horizontal divider line.", "Props: (none)"),
    "Spinner": ("<UI.Spinner>", "Loading spinner indicator.", "Props: size=sm|md|lg"),
    "Badge": ("<UI.Badge>", "Small status badge/tag.", "Props: color=str, children"),
    "DataGrid": ("<UI.DataGrid>", "Alias for Table with data/columns props.", "Props: data=list, columns=list"),
    "Chart": ("<UI.Chart>", "SVG bar or line chart.", "Props: type=bar|line, data=list, height=int"),
    "Toast": ("<UI.Toast>", "Temporary notification popup.", "Props: message=str, type=info|success|error, visible=bool"),
    "Tabs": ("<UI.Tabs>", "Tab navigation bar.", "Props: tabs=list, activeTab=str, onChange=fn"),
    "Dropdown": ("<UI.Dropdown>", "Clickable dropdown menu.", "Props: label=str, options=list, onSelect=fn"),
    "Accordion": ("<UI.Accordion>", "Collapsible content section.", "Props: title=str, children"),
    "Calendar": ("<UI.Calendar>", "Date picker calendar widget.", "Props: value=Date, onChange=fn"),
    "Chatbot": ("<UI.Chatbot>", "AI chat agent interface.", "Props: endpoint=str, placeholder=str"),
    "NetworkStatus": ("<UI.NetworkStatus>", "Online/offline status indicator.", "Props: (none)"),
    "useAuth": ("UI.useAuth()", "Authentication hook returning {user, login, logout, isAuthenticated}.", "Returns: { user, login(username, password), logout(), isAuthenticated }"),
}

_HOOK_DOCS = {
    "use_state": ("use_state(initial_value)", "Component state hook. Compiles to React.useState.", "Returns: [value, setter]  |  Example: count, set_count = use_state(0)"),
    "use_effect": ("use_effect(def(): ..., [deps])", "Side-effect hook. Compiles to React.useEffect.", "Params: callback function, dependency array  |  Example: use_effect(def(): document.title = 'Hi', [])"),
    "use_sync_state": ("use_sync_state(key, initial)", "Real-time synced state via WebSocket. Compiles to shared state subscription.", "Returns: [value, setter]  |  Example: messages, set_messages = use_sync_state('messages', [])"),
    "use_ref": ("ref = use_ref(initial)", "Mutable ref hook. Compiles to React.useRef.", "Access via ref.current  |  Example: player = use_ref(None)  →  player.current.play()"),
    "use_memo": ("val = use_memo(def(): expr, [deps])", "Memoized value hook. Compiles to React.useMemo.", "Example: filtered = use_memo(def(): [x for x in items if x.active], [items])"),
    "use_callback": ("fn = use_callback(def(): ..., [deps])", "Memoized callback hook. Compiles to React.useCallback.", "Example: on_click = use_callback(def(): do_thing(), [dep])"),
    "use_reducer": ("state, dispatch = use_reducer(reducer, initial)", "Reducer-based state hook. Compiles to React.useReducer.", "Example: count, dispatch = use_reducer(reducer, 0)  |  dispatch({'type': 'inc'})"),
}

_BLOCK_DOCS = {
    "server": ("server { ... }", "Backend server functions block. Each 'def' becomes a Flask API endpoint at /api/name.", "Functions are called from frontend via server.funcName(payload)"),
    "component": ("component Name():", "Frontend UI component. Compiles to a React function component.", "Must start with uppercase. Use use_state/use_effect inside."),
    "style": ("style { ... }", "CSS design tokens / variables block.", "Define colors, fonts, spacing as key: value pairs. Accessed via var(--key)."),
    "model": ("model Name { ... }", "Database model definition. Compiles to SQLAlchemy model.", "Fields use type syntax: name str, age int, created_at datetime"),
    "database": ("database { ... }", "Database configuration block.", "Sets engine, url, and other connection settings."),
    "dependencies": ("dependencies { ... }", "Python package dependencies block.", "Lists pip packages needed by the backend."),
    "shared_state": ("shared_state { ... }", "Global real-time state block. Variables sync across all clients via WebSocket.", "Access from frontend via shared.varName."),
    "realtime": ("realtime { ... }", "WebSocket realtime communication block.", "Define event handlers for live updates."),
    "middleware": ("middleware { ... }", "Request middleware block. Compiles to Flask @app.before_request.", "Functions receive 'request' object. Return dict to abort, or None to continue."),
    "pages": ("pages { ... }", "File-system routing configuration block.", "Define URL routes mapped to components."),
}
import sys
import json
import re

class PyReactLspServer:
    def __init__(self):
        self.documents = {}

    def run(self):
        # Set sys.stdin and sys.stdout to binary mode to handle \r\n cleanly on Windows
        try:
            import msvcrt
            import os
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        except (ImportError, AttributeError):
            pass

        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer
        
        while True:
            try:
                # Read headers
                header_line = b""
                content_length = 0
                while True:
                    char = stdin.read(1)
                    if not char:
                        return
                    header_line += char
                    if header_line.endswith(b"\r\n\r\n"):
                        break
                
                # Parse content length from headers
                headers = header_line.decode("utf-8")
                for line in headers.split("\r\n"):
                    if line.startswith("Content-Length:"):
                        content_length = int(line.split(":")[1].strip())

                # Read JSON body
                body = stdin.read(content_length)
                if not body:
                    return
                
                request = json.loads(body.decode("utf-8"))
                response = self.handle_request(request)
                if response:
                    res_body = json.dumps(response).encode("utf-8")
                    stdout.write(f"Content-Length: {len(res_body)}\r\n\r\n".encode("utf-8"))
                    stdout.write(res_body)
                    stdout.flush()
            except Exception as e:
                sys.stderr.write(f"LSP Error: {str(e)}\n")
                sys.stderr.flush()

    def handle_request(self, req):
        method = req.get("method")
        params = req.get("params", {})
        req_id = req.get("id")

        if method == "initialize":
            return {
                "id": req_id,
                "jsonrpc": "2.0",
                "result": {
                    "capabilities": {
                        "textDocumentSync": 1, # Full sync
                        "completionProvider": {
                            "triggerCharacters": ["."]
                        },
                        "hoverProvider": True,
                        "definitionProvider": True,
                        "codeActionProvider": True
                    }
                }
            }
        elif method == "textDocument/didOpen":
            uri = params.get("textDocument", {}).get("uri")
            text = params.get("textDocument", {}).get("text", "")
            self.documents[uri] = text
            self.validate_document(uri)
        elif method == "textDocument/didChange":
            uri = params.get("textDocument", {}).get("uri")
            content_changes = params.get("contentChanges", [])
            if content_changes:
                self.documents[uri] = content_changes[0].get("text", "")
            self.validate_document(uri)
        elif method == "textDocument/didSave":
            uri = params.get("textDocument", {}).get("uri")
            self.validate_document(uri)
        elif method == "textDocument/definition":
            uri = params.get("textDocument", {}).get("uri")
            position = params.get("position", {})
            line_idx = position.get("line", 0)
            col_idx = position.get("character", 0)
            
            text = self.documents.get(uri, "")
            lines = text.splitlines()
            if line_idx >= len(lines):
                return {"id": req_id, "jsonrpc": "2.0", "result": None}
                
            current_line = lines[line_idx]
            
            # Extract word under cursor
            start_col = col_idx
            while start_col > 0 and (current_line[start_col-1].isalnum() or current_line[start_col-1] == "_"):
                start_col -= 1
            end_col = col_idx
            while end_col < len(current_line) and (current_line[end_col].isalnum() or current_line[end_col] == "_"):
                end_col += 1
            word = current_line[start_col:end_col]
            
            target_line = -1
            target_col = -1
            
            if word:
                # Find definition of word inside text
                for idx, line in enumerate(lines):
                    # Check for def word(
                    if re.search(r'\bdef\s+' + re.escape(word) + r'\s*\(', line):
                        target_line = idx
                        target_col = line.find("def " + word) + 4
                        break
                    # Check for component word()
                    elif re.search(r'\bcomponent\s+' + re.escape(word) + r'\s*\(', line):
                        target_line = idx
                        target_col = line.find("component " + word) + 10
                        break
                        
            if target_line != -1:
                return {
                    "id": req_id,
                    "jsonrpc": "2.0",
                    "result": {
                        "uri": uri,
                        "range": {
                            "start": {"line": target_line, "character": target_col},
                            "end": {"line": target_line, "character": target_col + len(word)}
                        }
                    }
                }
            return {"id": req_id, "jsonrpc": "2.0", "result": None}

        elif method == "textDocument/hover":
            uri = params.get("textDocument", {}).get("uri")
            position = params.get("position", {})
            line_idx = position.get("line", 0)
            col_idx = position.get("character", 0)
            
            text = self.documents.get(uri, "")
            lines = text.splitlines()
            if line_idx >= len(lines):
                return {"id": req_id, "jsonrpc": "2.0", "result": None}
                
            current_line = lines[line_idx]
            
            # Extract word under cursor
            start_col = col_idx
            while start_col > 0 and (current_line[start_col-1].isalnum() or current_line[start_col-1] == "_"):
                start_col -= 1
            end_col = col_idx
            while end_col < len(current_line) and (current_line[end_col].isalnum() or current_line[end_col] == "_"):
                end_col += 1
            word = current_line[start_col:end_col]
            
            hover_content = None
            
            if word:
                # Check UI.Component hover
                line_before = current_line[:col_idx].rstrip()
                if line_before.endswith("UI."):
                    if word in _UI_COMPONENT_DOCS:
                        sig, desc, props = _UI_COMPONENT_DOCS[word]
                        hover_content = f"**{sig}**\n\n{desc}\n\n{props}"
                
                # Check hook hover
                if word in _HOOK_DOCS:
                    sig, desc, example = _HOOK_DOCS[word]
                    hover_content = f"**{sig}**\n\n{desc}\n\n{example}"
                
                # Check block keyword hover
                if word in _BLOCK_DOCS:
                    sig, desc, extra = _BLOCK_DOCS[word]
                    hover_content = f"**{sig}**\n\n{desc}\n\n{extra}"
                
                # Check server.function() hover
                if line_before.endswith("server.") or ("server." in current_line and word in self.extract_server_functions(text)):
                    hover_content = f"**server.{word}(payload)**\n\nBackend RPC endpoint. Compiles to POST /api/{word}.\n\nCall from frontend: `const result = await server.{word}({{ key: value }})`"
                
                # Check shared.variable hover
                if line_before.endswith("shared.") or ("shared." in current_line and word in self.extract_shared_vars(text)):
                    hover_content = f"**shared.{word}**\n\nGlobal shared state variable. Synced in real-time across all clients.\n\nAccess: `shared.{word}`  |  Set: `set_{word}(newValue)`"
            
            if hover_content:
                return {
                    "id": req_id,
                    "jsonrpc": "2.0",
                    "result": {
                        "contents": {
                            "kind": "markdown",
                            "value": hover_content
                        },
                        "range": {
                            "start": {"line": line_idx, "character": start_col},
                            "end": {"line": line_idx, "character": end_col}
                        }
                    }
                }
            return {"id": req_id, "jsonrpc": "2.0", "result": None}

        elif method == "textDocument/codeAction":
            uri = params.get("textDocument", {}).get("uri")
            diagnostics = params.get("context", {}).get("diagnostics", [])
            actions = []
            
            for diag in diagnostics:
                if diag.get("code") == "capitalize_component":
                    msg = diag.get("message")
                    comp_name_match = re.search(r"name '([^']+)'", msg)
                    if comp_name_match:
                        old_name = comp_name_match.group(1)
                        new_name = old_name.capitalize()
                        actions.append({
                            "title": f"Capitalize component to '{new_name}'",
                            "kind": "quickfix",
                            "diagnostics": [diag],
                            "edit": {
                                "changes": {
                                    uri: [
                                        {
                                            "range": diag.get("range"),
                                            "newText": new_name
                                        }
                                    ]
                                }
                            }
                        })
            return {
                "id": req_id,
                "jsonrpc": "2.0",
                "result": actions
            }

        elif method == "textDocument/completion":
            uri = params.get("textDocument", {}).get("uri")
            position = params.get("position", {})
            line_idx = position.get("line", 0)
            col_idx = position.get("character", 0)
            
            text = self.documents.get(uri, "")
            lines = text.splitlines()
            current_line = lines[line_idx] if line_idx < len(lines) else ""
            
            typed = current_line[:col_idx]
            completions = []
            
            # 1. Autocomplete server RPC calls: server.
            if typed.endswith("server."):
                server_funcs = self.extract_server_functions(text)
                for func in server_funcs:
                    completions.append({
                        "label": func,
                        "kind": 3,
                        "detail": f"Backend RPC: server.{func}()",
                        "insertText": f"{func}("
                    })
            
            # 2. Autocomplete UI elements: UI.
            elif typed.endswith("UI."):
                for comp_name, (sig, desc, props) in _UI_COMPONENT_DOCS.items():
                    kind = 3 if comp_name == "useAuth" else 7
                    completions.append({
                        "label": comp_name,
                        "kind": kind,
                        "detail": f"{sig} - {desc}",
                        "documentation": props,
                        "insertText": comp_name
                    })

            # 3. Autocomplete shared state variables: shared.
            elif typed.endswith("shared."):
                shared_vars = self.extract_shared_vars(text)
                for var in shared_vars:
                    completions.append({
                        "label": var,
                        "kind": 6,
                        "detail": f"Global State: shared.{var}",
                        "insertText": var
                    })
                    
            # 4. Autocomplete db helper calls: db.
            elif typed.endswith("db."):
                db_methods = ["session", "create_all", "drop_all", "metadata"]
                for method in db_methods:
                    completions.append({
                        "label": method,
                        "kind": 2,
                        "detail": f"Database Helper: db.{method}",
                        "insertText": method
                    })
            
            # 5. Fallback default keywords and React hooks
            elif not typed or typed[-1].isspace() or typed[-1] in ("{", "(", ","):
                keywords = ["server", "component", "style", "model", "database", "dependencies", "shared_state", "realtime", "middleware"]
                for kw in keywords:
                    completions.append({
                        "label": kw,
                        "kind": 14,
                        "detail": f"PyReact Block: {kw}"
                    })
                hooks = ["use_state", "use_effect", "use_sync_state", "use_ref", "use_memo", "use_callback", "use_reducer"]
                for hook in hooks:
                    completions.append({
                        "label": hook,
                        "kind": 3,
                        "detail": f"PyReact Hook: {hook}()",
                        "insertText": f"{hook}("
                    })
            
            return {
                "id": req_id,
                "jsonrpc": "2.0",
                "result": completions
            }
        
        return None

    def validate_document(self, uri):
        """Perform validation and publish diagnostics to client."""
        text = self.documents.get(uri, "")
        diagnostics = []
        try:
            from pyreact.compiler.lexer import Lexer
            from pyreact.compiler.parser import Parser, ParseError
            
            lexer = Lexer(text)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            # Check lowercase component naming
            for comp in ast.components:
                if comp.name and not comp.name[0].isupper():
                    comp_line = 0
                    for idx, line in enumerate(text.splitlines()):
                        if f"component {comp.name}" in line:
                            comp_line = idx
                            break
                    diagnostics.append({
                        "range": {
                            "start": {"line": comp_line, "character": 10},
                            "end": {"line": comp_line, "character": 10 + len(comp.name)}
                        },
                        "severity": 2, # Warning
                        "message": f"Component name '{comp.name}' should start with an uppercase letter.",
                        "source": "pyreact",
                        "code": "capitalize_component"
                    })

            # Anti-pattern detection: React hooks & patterns that should be PyReact
            _ANTIPATTERNS = [
                (r'\buseState\s*\(', "useState() terdeteksi. Gunakan PyReact: `val, setVal = use_state(initial)`", "use_useState"),
                (r'\buseEffect\s*\(', "useEffect() terdeteksi. Gunakan PyReact: `use_effect(def(): ..., [deps])`", "use_useEffect"),
                (r'\buseRef\s*\(', "useRef() terdeteksi. Gunakan PyReact: `ref = use_ref(None)`", "use_useRef"),
                (r'\buseMemo\s*\(', "useMemo() terdeteksi. Gunakan PyReact: `val = use_memo(def(): expr, [deps])`", "use_useMemo"),
                (r'\buseCallback\s*\(', "useCallback() terdeteksi. Gunakan PyReact: `fn = use_callback(def(): ..., [deps])`", "use_useCallback"),
                (r'\buseReducer\s*\(', "useReducer() terdeteksi. Gunakan PyReact: `state, dispatch = use_reducer(reducer, initial)`", "use_useReducer"),
                (r'\bfetch\s*\(', "fetch() terdeteksi. Gunakan PyReact PyBridge: `result = server.func_name(args)`", "use_fetch"),
                (r'\baxios\b', "axios terdeteksi. Gunakan PyReact PyBridge: `result = server.func_name(args)`", "use_axios"),
                (r'export\s+default\s+function', "export default function terdeteksi. Gunakan PyReact: `component Name():`", "use_export_default"),
                (r'import\s+React\b', "import React tidak diperlukan di PyReact. Hapus baris ini.", "no_import_react"),
            ]
            import re as _lsp_re
            for line_no, line_text in enumerate(text.splitlines()):
                for pattern, message, code in _ANTIPATTERNS:
                    if _lsp_re.search(pattern, line_text):
                        col = line_text.find(line_text.lstrip())
                        diagnostics.append({
                            "range": {
                                "start": {"line": line_no, "character": col},
                                "end": {"line": line_no, "character": len(line_text.rstrip())}
                            },
                            "severity": 2,  # Warning
                            "message": f"[PyReact Hint] {message}",
                            "source": "pyreact",
                            "code": code
                        })
                        break  # one warning per line
        except ParseError as e:
            line = max(0, e.line - 1)
            col = max(0, e.col - 1)
            diagnostics.append({
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": col + 5}
                },
                "severity": 1, # Error
                "message": str(e),
                "source": "pyreact"
            })
        except Exception as e:
            # General compilation failure
            diagnostics.append({
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 10}
                },
                "severity": 1, # Error
                "message": f"LSP Validation Warning: {str(e)}",
                "source": "pyreact"
            })

        # Send publishDiagnostics notification to client
        notification = {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics
            }
        }
        res_body = json.dumps(notification).encode("utf-8")
        sys.stdout.buffer.write(f"Content-Length: {len(res_body)}\r\n\r\n".encode("utf-8"))
        sys.stdout.buffer.write(res_body)
        sys.stdout.buffer.flush()

    def extract_server_functions(self, text):
        funcs = []
        server_match = re.search(r'server\s*\{([^}]+)\}', text, re.DOTALL)
        if server_match:
            body = server_match.group(1)
            funcs = re.findall(r'def\s+(\w+)\s*\(', body)
        return funcs

    def extract_shared_vars(self, text):
        vars_list = []
        shared_match = re.search(r'shared_state\s*\{([^}]+)\}', text, re.DOTALL)
        if shared_match:
            body = shared_match.group(1)
            vars_list = re.findall(r'(\w+)\s*=', body)
        return vars_list

if __name__ == "__main__":
    server = PyReactLspServer()
    server.run()
