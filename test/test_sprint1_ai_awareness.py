"""Test suite for PyReact v2.0 Sprint 1: AI Language Awareness features.
Tests: LLMS.txt, .pyreact.code-snippets, pyreact convert, LSP anti-pattern hints.
"""
import unittest
import shutil
import json
from pathlib import Path
from unittest.mock import patch
from pyreact.cli import (
    _generate_llms_txt,
    _generate_vscode_snippets,
    cmd_convert,
    cmd_init,
)


class TestLLMSTxt(unittest.TestCase):
    """A1: LLMS.txt generator"""

    def test_generates_non_empty_content(self):
        content = _generate_llms_txt()
        self.assertIsInstance(content, str)
        self.assertGreater(len(content), 100)

    def test_contains_critical_do_donts(self):
        content = _generate_llms_txt()
        self.assertIn("use_state", content)
        self.assertIn("useState", content)
        self.assertIn("server.", content)
        self.assertIn("fetch(", content)
        self.assertIn("component", content)
        self.assertIn("export default function", content)

    def test_syntax_map_section(self):
        content = _generate_llms_txt()
        self.assertIn("== SYNTAX MAP ==", content)
        self.assertIn("None", content)
        self.assertIn("True / False", content)

    def test_block_syntax_section(self):
        content = _generate_llms_txt()
        self.assertIn("== BLOCK SYNTAX ==", content)
        self.assertIn("server { }", content)
        self.assertIn("component Name():", content)
        self.assertIn("pages { }", content)

    def test_created_in_project_by_init_wizard(self):
        project = Path("test-llms-wizard")
        if project.exists():
            shutil.rmtree(project)
        try:
            with patch("builtins.input", side_effect=["test-llms-wizard", "1", "n", "n", "n"]):
                cmd_init([])
            self.assertTrue((project / "LLMS.txt").exists())
            content = (project / "LLMS.txt").read_text(encoding="utf-8")
            self.assertIn("use_state", content)
        finally:
            if project.exists():
                shutil.rmtree(project)


class TestVSCodeSnippets(unittest.TestCase):
    """A4: .pyreact.code-snippets generator"""

    def test_generates_valid_json(self):
        content = _generate_vscode_snippets()
        parsed = json.loads(content)
        self.assertIsInstance(parsed, dict)

    def test_has_required_snippets(self):
        parsed = json.loads(_generate_vscode_snippets())
        self.assertIn("PyReact Component", parsed)
        self.assertIn("PyReact Server Block", parsed)
        self.assertIn("PyReact CRUD Full", parsed)
        self.assertIn("PyReact use_state", parsed)
        self.assertIn("PyReact use_effect", parsed)
        self.assertIn("PyReact server call", parsed)

    def test_comp_snippet_prefix(self):
        parsed = json.loads(_generate_vscode_snippets())
        self.assertEqual(parsed["PyReact Component"]["prefix"], "comp")

    def test_crud_snippet_has_database_block(self):
        parsed = json.loads(_generate_vscode_snippets())
        body = "\n".join(parsed["PyReact CRUD Full"]["body"])
        self.assertIn("database {", body)
        self.assertIn("use_state", body)
        self.assertIn("server.", body)

    def test_created_in_project_by_init_wizard(self):
        project = Path("test-snippets-wizard")
        if project.exists():
            shutil.rmtree(project)
        try:
            with patch("builtins.input", side_effect=["test-snippets-wizard", "1", "n", "n", "n"]):
                cmd_init([])
            snippets_file = project / ".pyreact.code-snippets"
            self.assertTrue(snippets_file.exists())
            parsed = json.loads(snippets_file.read_text(encoding="utf-8"))
            self.assertIn("PyReact Component", parsed)
        finally:
            if project.exists():
                shutil.rmtree(project)


class TestCmdConvert(unittest.TestCase):
    """A3: pyreact convert <file.jsx>"""

    def setUp(self):
        self.src = Path("_test_convert_input.jsx")

    def tearDown(self):
        for f in Path(".").glob("_test_convert_input*"):
            f.unlink(missing_ok=True)

    def _write(self, content):
        self.src.write_text(content, encoding="utf-8")

    def _convert(self):
        cmd_convert([str(self.src)])
        out = self.src.with_suffix(".pyreact")
        return out.read_text(encoding="utf-8")

    def test_converts_usestate(self):
        self._write("const [count, setCount] = useState(0);")
        result = self._convert()
        self.assertIn("use_state(0)", result)
        self.assertNotIn("useState", result)

    def test_converts_usestate_null(self):
        self._write("const [data, setData] = useState(null);")
        result = self._convert()
        self.assertIn("use_state(None)", result)

    def test_converts_useref(self):
        self._write("const myRef = useRef(null);")
        result = self._convert()
        self.assertIn("use_ref(None)", result)
        self.assertNotIn("useRef", result)

    def test_converts_fetch(self):
        self._write('const res = fetch("/api/get_users", {method:"POST"});')
        result = self._convert()
        self.assertIn("server.get_users()", result)

    def test_converts_export_default_function(self):
        self._write("export default function MyPage() {")
        result = self._convert()
        self.assertIn("component MyPage():", result)
        self.assertNotIn("export default function", result)

    def test_removes_react_import(self):
        self._write("import React from 'react';\nimport { useState } from 'react';")
        result = self._convert()
        self.assertNotIn("import React", result)
        self.assertNotIn('from "react"', result)

    def test_converts_null_true_false(self):
        self._write("const x = null; const y = true; const z = false;")
        result = self._convert()
        self.assertIn("None", result)
        self.assertIn("True", result)
        self.assertIn("False", result)
        self.assertNotIn(" null", result)

    def test_output_file_created(self):
        self._write("const [x, setX] = useState(0);")
        cmd_convert([str(self.src)])
        out = self.src.with_suffix(".pyreact")
        self.assertTrue(out.exists())

    def test_no_args_exits(self):
        with self.assertRaises(SystemExit):
            cmd_convert([])

    def test_missing_file_exits(self):
        with self.assertRaises(SystemExit):
            cmd_convert(["nonexistent_file_xyz.jsx"])


class TestLSPAntiPatternHints(unittest.TestCase):
    """A2: LSP anti-pattern detection logic"""

    # Replicate the anti-pattern list from lsp.py for unit testing
    _ANTIPATTERNS = [
        (r'\buseState\s*\(', "use_useState"),
        (r'\buseEffect\s*\(', "use_useEffect"),
        (r'\buseRef\s*\(', "use_useRef"),
        (r'\buseMemo\s*\(', "use_useMemo"),
        (r'\buseCallback\s*\(', "use_useCallback"),
        (r'\buseReducer\s*\(', "use_useReducer"),
        (r'\bfetch\s*\(', "use_fetch"),
        (r'\baxios\b', "use_axios"),
        (r'export\s+default\s+function', "use_export_default"),
        (r'import\s+React\b', "no_import_react"),
    ]

    def _check_code(self, code):
        """Return list of (code, line_no) for anti-patterns found."""
        import re as _re
        results = []
        for line_no, line_text in enumerate(code.splitlines()):
            for pattern, code_tag in self._ANTIPATTERNS:
                if _re.search(pattern, line_text):
                    results.append((code_tag, line_no))
                    break
        return results

    def test_detects_usestate_antipattern(self):
        found = self._check_code("const [x, setX] = useState(0);")
        codes = [c for c, _ in found]
        self.assertIn("use_useState", codes)

    def test_detects_fetch_antipattern(self):
        found = self._check_code('const r = fetch("/api/data");')
        codes = [c for c, _ in found]
        self.assertIn("use_fetch", codes)

    def test_detects_export_default_antipattern(self):
        found = self._check_code("export default function App() {}")
        codes = [c for c, _ in found]
        self.assertIn("use_export_default", codes)

    def test_detects_axios_antipattern(self):
        found = self._check_code("const r = axios.get('/api/data');")
        codes = [c for c, _ in found]
        self.assertIn("use_axios", codes)

    def test_detects_import_react_antipattern(self):
        found = self._check_code("import React from 'react';")
        codes = [c for c, _ in found]
        self.assertIn("no_import_react", codes)

    def test_no_false_positives_on_valid_pyreact(self):
        valid_code = """
component App():
    count, setCount = use_state(0)

    def handle():
        res = server.get_data()
        setCount(res["count"])

    return (
        <UI.Page>
            <UI.Button onClick={handle}>Click</UI.Button>
        </UI.Page>
    )
"""
        found = self._check_code(valid_code)
        ap_codes = {"use_useState", "use_useEffect", "use_fetch", "use_export_default", "no_import_react"}
        bad = [(c, ln) for c, ln in found if c in ap_codes]
        self.assertEqual(bad, [], f"False positives: {bad}")

    def test_lsp_hook_docs_contain_new_hooks(self):
        from pyreact.compiler.lsp import _HOOK_DOCS
        self.assertIn("use_ref", _HOOK_DOCS)
        self.assertIn("use_memo", _HOOK_DOCS)
        self.assertIn("use_callback", _HOOK_DOCS)
        self.assertIn("use_reducer", _HOOK_DOCS)



if __name__ == "__main__":
    unittest.main()
