"""Test suite for PyReact v2.0 Sprint 2 (React Parity Hooks) & Sprint 3 (DX Tooling).
Tests: use_ref, use_memo, use_callback, use_reducer parsing + codegen, pyreact lint, pyreact format.
"""
import unittest
import shutil
import os
from pathlib import Path
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import (
    Parser, RefVar, MemoVar, CallbackVar, ReducerVar, HookNode
)
from pyreact.compiler.codegen import CodeGenerator
from pyreact.cli import cmd_lint, cmd_format


# ── Sprint 2: React Parity Hook Parsing ───────────────────────────────────────

def _parse(src: str):
    tokens = Lexer(src).tokenize()
    return Parser(tokens).parse()


def _compile(src: str) -> str:
    ast = _parse(src)
    cg = CodeGenerator(ast)
    # Compile each component individually to avoid needing full project context
    parts = []
    for comp in ast.components:
        parts.append(cg._gen_component_file(comp))
    return "\n".join(parts)


COMP_USE_REF = """
component VideoPlayer():
    player_ref = use_ref(None)

    def play():
        player_ref.current.play()

    return (
        <UI.Page>
            <UI.Button onClick={play}>Play</UI.Button>
        </UI.Page>
    )
"""

COMP_USE_REDUCER = """
component Counter():
    def reducer(state, action):
        if action["type"] == "inc":
            return state + 1
        return state

    count, dispatch = use_reducer(reducer, 0)

    return (
        <UI.Page>
            <UI.Text>{count}</UI.Text>
        </UI.Page>
    )
"""

COMP_USE_MEMO = """
component FilteredList():
    items, setItems = use_state([])
    query, setQuery = use_state("")

    filtered = use_memo(def(): items, [items, query])

    return (
        <UI.Page>
            <UI.Text>{filtered}</UI.Text>
        </UI.Page>
    )
"""

COMP_USE_CALLBACK = """
component Search():
    query, setQuery = use_state("")

    on_search = use_callback(def(): server.search(query), [query])

    return (
        <UI.Page>
            <UI.Button onClick={on_search}>Search</UI.Button>
        </UI.Page>
    )
"""


class TestUseRef(unittest.TestCase):
    def test_parser_detects_use_ref(self):
        ast = _parse(COMP_USE_REF)
        self.assertEqual(len(ast.components), 1)
        comp = ast.components[0]
        self.assertEqual(len(comp.refs), 1)
        self.assertEqual(comp.refs[0].name, "player_ref")
        self.assertEqual(comp.refs[0].initial, "None")

    def test_codegen_emits_useref(self):
        output = _compile(COMP_USE_REF)
        self.assertIn("React.useRef", output)
        self.assertIn("player_ref", output)


class TestUseReducer(unittest.TestCase):
    def test_parser_detects_use_reducer(self):
        ast = _parse(COMP_USE_REDUCER)
        comp = ast.components[0]
        self.assertEqual(len(comp.reducers), 1)
        rv = comp.reducers[0]
        self.assertEqual(rv.state, "count")
        self.assertEqual(rv.dispatch, "dispatch")
        self.assertEqual(rv.reducer, "reducer")
        self.assertEqual(rv.initial, "0")

    def test_codegen_emits_usereducer(self):
        output = _compile(COMP_USE_REDUCER)
        self.assertIn("React.useReducer", output)
        self.assertIn("count", output)
        self.assertIn("dispatch", output)


class TestUseMemo(unittest.TestCase):
    def test_parser_detects_use_memo(self):
        ast = _parse(COMP_USE_MEMO)
        comp = ast.components[0]
        self.assertEqual(len(comp.memos), 1)
        mv = comp.memos[0]
        self.assertEqual(mv.name, "filtered")
        self.assertIn("[items, query]", mv.deps)

    def test_codegen_emits_usememo(self):
        output = _compile(COMP_USE_MEMO)
        self.assertIn("React.useMemo", output)
        self.assertIn("filtered", output)


class TestUseCallback(unittest.TestCase):
    def test_parser_detects_use_callback(self):
        ast = _parse(COMP_USE_CALLBACK)
        comp = ast.components[0]
        self.assertEqual(len(comp.callbacks), 1)
        cb = comp.callbacks[0]
        self.assertEqual(cb.name, "on_search")
        self.assertIn("[query]", cb.deps)

    def test_codegen_emits_usecallback(self):
        output = _compile(COMP_USE_CALLBACK)
        self.assertIn("React.useCallback", output)
        self.assertIn("on_search", output)


class TestASTNodesExist(unittest.TestCase):
    """Sprint 2: verify all new AST node types are importable and instantiable."""

    def test_refvar_instantiable(self):
        r = RefVar(name="myRef", initial="null")
        self.assertEqual(r.name, "myRef")

    def test_memovar_instantiable(self):
        m = MemoVar(name="filtered", expr="items", deps="[items]")
        self.assertEqual(m.name, "filtered")

    def test_callbackvar_instantiable(self):
        c = CallbackVar(name="onClick", body="doThing()", deps="[dep]")
        self.assertEqual(c.name, "onClick")

    def test_reducervar_instantiable(self):
        r = ReducerVar(state="count", dispatch="dispatch", reducer="reducer", initial="0")
        self.assertEqual(r.state, "count")

    def test_hooknode_instantiable(self):
        h = HookNode(name="useMyHook", raw_body="return {}")
        self.assertEqual(h.name, "useMyHook")

    def test_programnode_has_hooks_list(self):
        ast = _parse("server { def ping(): return {} }")
        self.assertIsInstance(ast.hooks, list)

    def test_componentnode_has_new_fields(self):
        ast = _parse(COMP_USE_REF)
        comp = ast.components[0]
        self.assertIsInstance(comp.refs, list)
        self.assertIsInstance(comp.memos, list)
        self.assertIsInstance(comp.callbacks, list)
        self.assertIsInstance(comp.reducers, list)


# ── Sprint 3: pyreact lint ─────────────────────────────────────────────────────

class TestCmdLint(unittest.TestCase):
    def setUp(self):
        self.test_file = Path("_lint_test.pyreact")

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def _write(self, content):
        self.test_file.write_text(content, encoding="utf-8")

    def test_no_issues_on_valid_pyreact(self):
        self._write("""
component MyApp():
    count, setCount = use_state(0)

    def handle():
        res = server.get_data()
        setCount(res)

    return (<UI.Page><UI.Text>{count}</UI.Text></UI.Page>)
""")
        # Should not raise SystemExit
        try:
            cmd_lint([str(self.test_file)])
        except SystemExit:
            self.fail("lint raised SystemExit on valid PyReact code")

    def test_detects_usestate(self):
        self._write("const [x, setX] = useState(0);")
        with self.assertRaises(SystemExit):
            cmd_lint([str(self.test_file)])

    def test_detects_fetch(self):
        self._write("const r = fetch('/api/data');")
        with self.assertRaises(SystemExit):
            cmd_lint([str(self.test_file)])

    def test_detects_export_default(self):
        self._write("export default function App() {}")
        with self.assertRaises(SystemExit):
            cmd_lint([str(self.test_file)])

    def test_skips_comment_lines(self):
        self._write("# const [x, setX] = useState(0); -- this is a comment\n")
        # Should not detect issues in comment lines
        try:
            cmd_lint([str(self.test_file)])
        except SystemExit:
            self.fail("lint incorrectly flagged a comment line")

    def test_warning_only_does_not_exit(self):
        self._write("# Valid pyreact with only warnings\nimport React from 'react';\n")
        try:
            cmd_lint([str(self.test_file)])
        except SystemExit:
            self.fail("warnings (W001) should not cause SystemExit")


# ── Sprint 3: pyreact format ───────────────────────────────────────────────────

class TestCmdFormat(unittest.TestCase):
    def setUp(self):
        self.test_file = Path("_format_test.pyreact")

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def _write(self, content):
        self.test_file.write_text(content, encoding="utf-8")
        return content

    def _format(self):
        cmd_format([str(self.test_file)])
        return self.test_file.read_text(encoding="utf-8")

    def test_removes_trailing_whitespace(self):
        self._write("component App():   \n    x, setX = use_state(0)   \n")
        result = self._format()
        for line in result.splitlines():
            self.assertEqual(line, line.rstrip(), f"Trailing whitespace found: {line!r}")

    def test_file_ends_with_single_newline(self):
        self._write("component App():\n    pass\n\n\n")
        result = self._format()
        self.assertTrue(result.endswith('\n'))
        self.assertFalse(result.endswith('\n\n'))

    def test_no_more_than_3_consecutive_blank_lines(self):
        self._write("server {\n    def ping(): return {}\n}\n\n\n\n\n\ncomponent App():\n    pass\n")
        result = self._format()
        self.assertNotIn('\n\n\n\n', result)

    def test_check_mode_exits_on_unformatted(self):
        self._write("component App():   \n    x, setX = use_state(0)   \n")
        with self.assertRaises(SystemExit):
            cmd_format([str(self.test_file), '--check'])

    def test_check_mode_ok_on_clean_file(self):
        self._write("component App():\n    x, setX = use_state(0)\n")
        try:
            cmd_format([str(self.test_file), '--check'])
        except SystemExit:
            self.fail("format --check raised SystemExit on already-clean file")

    def test_sorts_style_block_alphabetically(self):
        self._write("""style {
    primary = "#6366f1"
    background = "#030712"
    font = "Inter"
}
""")
        result = self._format()
        style_match = __import__('re').search(r'style\s*\{([^}]+)\}', result)
        if style_match:
            keys = [l.strip().split('=')[0].strip()
                    for l in style_match.group(1).splitlines() if l.strip()]
            self.assertEqual(keys, sorted(keys), f"Style keys not sorted: {keys}")


if __name__ == "__main__":
    unittest.main()
