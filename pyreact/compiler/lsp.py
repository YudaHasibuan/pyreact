"""PYREACT Language Server Protocol (LSP) Server.
Handles auto-completions, blocks detection, cross-boundary definition jump, and real-time validation.
"""
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
                ui_components = ["Button", "Input", "Card", "Text", "Alert", "Table", "Chart", "Navbar", "Page", "DevTools"]
                for comp in ui_components:
                    completions.append({
                        "label": comp,
                        "kind": 7,
                        "detail": f"PyReact UI Component: <UI.{comp}>",
                        "insertText": comp
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
                keywords = ["server", "component", "style", "model", "database", "dependencies", "shared_state", "realtime"]
                for kw in keywords:
                    completions.append({
                        "label": kw,
                        "kind": 14,
                        "detail": f"PyReact Block: {kw}"
                    })
                hooks = ["use_state", "use_effect", "use_sync_state"]
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
