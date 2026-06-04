# Test suite for PyReact Fase 20: VS Code Extension Penuh
import unittest
import json
from pathlib import Path
from pyreact.compiler.lsp import PyReactLspServer

class TestFase20(unittest.TestCase):
    def setUp(self):
        self.extension_dir = Path("vscode-extension")

    def test_extension_package_json(self):
        # 1. Verify package.json contains all required elements
        pkg_file = self.extension_dir / "package.json"
        self.assertTrue(pkg_file.exists())
        
        with open(pkg_file, "r", encoding="utf-8") as f:
            pkg_data = json.load(f)
            
        self.assertEqual(pkg_data.get("name"), "pyreact-vscode")
        
        # Verify language contribution
        langs = pkg_data.get("contributes", {}).get("languages", [])
        self.assertTrue(any(l.get("id") == "pyreact" for l in langs))
        
        # Verify command contribution
        cmds = pkg_data.get("contributes", {}).get("commands", [])
        self.assertTrue(any(c.get("command") == "pyreact.showPreview" for c in cmds))

    def test_syntax_highlighting_embeds(self):
        # 2. Verify grammar file includes embeds for Python and JSX
        grammar_file = self.extension_dir / "syntaxes" / "pyreact.tmLanguage.json"
        self.assertTrue(grammar_file.exists())
        
        with open(grammar_file, "r", encoding="utf-8") as f:
            grammar = json.load(f)
            
        # Ensure python and js.jsx scopes are embedded
        patterns = grammar.get("patterns", [])
        self.assertTrue(any("source.python" in str(p) for p in patterns))
        self.assertTrue(any("source.js.jsx" in str(p) for p in patterns))

    def test_lsp_definition_jump(self):
        # 3. Verify cross-boundary definition resolver
        server = PyReactLspServer()
        uri = "file:///mock/app.pyreact"
        doc_text = """
        server {
            def greeting(name):
                return "Hello " + name
        }
        component Home():
            return <div onClick={() => server.greeting('Yuda')} />
        """
        server.documents[uri] = doc_text
        
        lines = doc_text.splitlines()
        current_line = lines[6]
        col_idx = current_line.find("greeting") + 2
        
        # Request definition for "greeting"
        req = {
            "id": 1,
            "method": "textDocument/definition",
            "params": {
                "textDocument": {"uri": uri},
                "position": {"line": 6, "character": col_idx}
            }
        }
        res = server.handle_request(req)
        self.assertIsNotNone(res)
        result = res.get("result")
        self.assertIsNotNone(result)
        # Should point to line 2 (def greeting)
        self.assertEqual(result["range"]["start"]["line"], 2)

    def test_lsp_code_actions_and_diagnostics(self):
        # 4. Verify diagnostic validation and capitalize quick-fix suggestion
        server = PyReactLspServer()
        uri = "file:///mock/app.pyreact"
        server.documents[uri] = """
        component home():
            return <div />
        """
        
        # We override validate_document stdout writing to capture diagnostic output
        captured_data = []
        import sys
        orig_write = sys.stdout.buffer.write
        def mock_write(b):
            captured_data.append(b)
            return len(b)
            
        sys.stdout.buffer.write = mock_write
        try:
            server.validate_document(uri)
        finally:
            sys.stdout.buffer.write = orig_write
            
        full_output = b"".join(captured_data)
        captured_diagnostics = []
        parts = full_output.split(b"\r\n\r\n", 1)
        if len(parts) > 1:
            try:
                data = json.loads(parts[1].decode("utf-8"))
                if data.get("method") == "textDocument/publishDiagnostics":
                    captured_diagnostics.append(data)
            except Exception as e:
                print("LSP Decode Error:", e)
            
        self.assertEqual(len(captured_diagnostics), 1)
        diag = captured_diagnostics[0]["params"]["diagnostics"][0]
        self.assertEqual(diag["code"], "capitalize_component")
        self.assertIn("should start with an uppercase letter", diag["message"])
        
        # Request code actions for that diagnostic
        req_actions = {
            "id": 2,
            "method": "textDocument/codeAction",
            "params": {
                "textDocument": {"uri": uri},
                "context": {"diagnostics": [diag]}
            }
        }
        res_actions = server.handle_request(req_actions)
        self.assertIsNotNone(res_actions)
        actions = res_actions.get("result")
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["title"], "Capitalize component to 'Home'")
        self.assertEqual(actions[0]["edit"]["changes"][uri][0]["newText"], "Home")

if __name__ == '__main__':
    unittest.main()
