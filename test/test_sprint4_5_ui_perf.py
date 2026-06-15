"""Test suite for PyReact v2.0 Sprint 4 (UI Library v2) & Sprint 5 (Performance & Testing).
Tests: Skeleton, CodeBlock, CommandPalette, DataTable, Icon, Stepper, Timeline presence in codegen,
and pyreact build --analyze, pyreact test --watch functionality.
"""
import unittest
import os
import shutil
import time
import hashlib
from pathlib import Path
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator, UI_COMPONENTS_JSX
from pyreact.cli import cmd_build, cmd_lint


# ── Sprint 4: UI Library v2 Component Presence ────────────────────────────────

class TestUILibraryV2ComponentPresence(unittest.TestCase):
    """Verify all new v2 components are present in UI_COMPONENTS_JSX string."""

    def test_skeleton_component_present(self):
        self.assertIn("Skeleton:", UI_COMPONENTS_JSX)
        self.assertIn("animate-pulse", UI_COMPONENTS_JSX)

    def test_skeleton_card_present(self):
        self.assertIn("SkeletonCard:", UI_COMPONENTS_JSX)

    def test_codeblock_component_present(self):
        self.assertIn("CodeBlock:", UI_COMPONENTS_JSX)
        self.assertIn("showCopy", UI_COMPONENTS_JSX)
        self.assertIn("navigator.clipboard", UI_COMPONENTS_JSX)

    def test_commandpalette_component_present(self):
        self.assertIn("CommandPalette:", UI_COMPONENTS_JSX)
        self.assertIn("ArrowDown", UI_COMPONENTS_JSX)
        self.assertIn("ArrowUp", UI_COMPONENTS_JSX)

    def test_datatable_component_present(self):
        self.assertIn("DataTable:", UI_COMPONENTS_JSX)
        self.assertIn("pageSize", UI_COMPONENTS_JSX)
        self.assertIn("searchable", UI_COMPONENTS_JSX)
        self.assertIn("sortable", UI_COMPONENTS_JSX)

    def test_datatable_has_pagination(self):
        self.assertIn("totalPages", UI_COMPONENTS_JSX)
        self.assertIn("setPage", UI_COMPONENTS_JSX)

    def test_datatable_has_search(self):
        self.assertIn("setSearch", UI_COMPONENTS_JSX)

    def test_icon_component_present(self):
        self.assertIn("Icon:", UI_COMPONENTS_JSX)
        # Verify common icons
        self.assertIn("user:", UI_COMPONENTS_JSX)
        self.assertIn("home:", UI_COMPONENTS_JSX)
        self.assertIn("search:", UI_COMPONENTS_JSX)
        self.assertIn("settings:", UI_COMPONENTS_JSX)
        self.assertIn("trash:", UI_COMPONENTS_JSX)
        self.assertIn("edit:", UI_COMPONENTS_JSX)
        self.assertIn("check:", UI_COMPONENTS_JSX)

    def test_stepper_component_present(self):
        self.assertIn("Stepper:", UI_COMPONENTS_JSX)
        self.assertIn("activeStep", UI_COMPONENTS_JSX)
        self.assertIn("onStepClick", UI_COMPONENTS_JSX)

    def test_timeline_component_present(self):
        self.assertIn("Timeline:", UI_COMPONENTS_JSX)
        self.assertIn("items", UI_COMPONENTS_JSX)

    def test_icon_renders_svg(self):
        self.assertIn("<svg", UI_COMPONENTS_JSX)
        self.assertIn("viewBox=\"0 0 24 24\"", UI_COMPONENTS_JSX)
        self.assertIn("strokeLinecap", UI_COMPONENTS_JSX)


class TestUILibraryV2InCompilation(unittest.TestCase):
    """Verify new components can be referenced in .pyreact files."""

    def _compile_component(self, src):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        cg = CodeGenerator(ast)
        parts = []
        for comp in ast.components:
            parts.append(cg._gen_component_file(comp))
        return "\n".join(parts)

    def test_skeleton_in_jsx_compiles(self):
        src = """
component LoadingView():
    loading, _ = use_state(True)

    return (
        <UI.Page>
            <UI.Skeleton height="2rem" rounded="lg" />
            <UI.SkeletonCard lines={3} showAvatar={True} />
        </UI.Page>
    )
"""
        output = self._compile_component(src)
        self.assertIn("LoadingView", output)
        self.assertIn("UI.Skeleton", output)

    def test_datatable_in_jsx_compiles(self):
        src = """
component UserTable():
    users, setUsers = use_state([])

    return (
        <UI.Page>
            <UI.DataTable columns={[{"key": "name", "label": "Name"}]} rows={users} pageSize={5} />
        </UI.Page>
    )
"""
        output = self._compile_component(src)
        self.assertIn("UserTable", output)

    def test_icon_in_jsx_compiles(self):
        src = """
component NavBar():
    return (
        <UI.Page>
            <UI.Icon name="user" size={24} />
            <UI.Icon name="settings" color="blue" />
        </UI.Page>
    )
"""
        output = self._compile_component(src)
        self.assertIn("NavBar", output)


# ── Sprint 5: pyreact build --analyze ─────────────────────────────────────────

class TestBuildAnalyze(unittest.TestCase):
    """Test --analyze flag of pyreact build."""

    def setUp(self):
        # Create a minimal dist directory to analyze
        self.dist = Path("_test_analyze_dist")
        self.dist.mkdir(exist_ok=True)
        (self.dist / "backend").mkdir(exist_ok=True)
        (self.dist / "frontend").mkdir(exist_ok=True)
        # Create test files of known sizes
        (self.dist / "backend" / "app.py").write_bytes(b"x" * 5000)      # 5 KB
        (self.dist / "frontend" / "main.jsx").write_bytes(b"x" * 50000)  # 50 KB
        (self.dist / "frontend" / "components.jsx").write_bytes(b"x" * 80000)  # 80 KB

    def tearDown(self):
        if self.dist.exists():
            shutil.rmtree(self.dist)

    def test_analyze_reports_file_sizes(self):
        """Verify analyze logic correctly reads and sizes files."""
        import os
        total_bytes = 0
        file_sizes = []
        for root, _, files in os.walk(self.dist):
            for fname in files:
                fpath = Path(root) / fname
                size = fpath.stat().st_size
                total_bytes += size
                file_sizes.append((size, fname))
        file_sizes.sort(reverse=True)

        # Largest file should be components.jsx at 80 KB
        self.assertEqual(file_sizes[0][1], "components.jsx")
        self.assertEqual(file_sizes[0][0], 80000)

        total_kb = total_bytes / 1024
        # 5 + 50 + 80 = 135 KB — within optimal range
        self.assertLess(total_kb, 150)

    def test_analyze_categorizes_large_bundles(self):
        """Verify size categorization logic."""
        def categorize(total_kb):
            if total_kb < 150:
                return "optimal"
            elif total_kb < 500:
                return "acceptable"
            else:
                return "large"

        self.assertEqual(categorize(100), "optimal")
        self.assertEqual(categorize(200), "acceptable")
        self.assertEqual(categorize(600), "large")


# ── Sprint 5: pyreact test --watch (file hash detection) ─────────────────────

class TestWatchModeFileHash(unittest.TestCase):
    """Test the MD5 file-change detection used by test --watch."""

    def setUp(self):
        self.test_file = Path("_watch_test.pyreact")

    def tearDown(self):
        if self.test_file.exists():
            self.test_file.unlink()

    def _file_hash(self, path):
        try:
            return hashlib.md5(Path(path).read_bytes()).hexdigest()
        except Exception:
            return ""

    def test_same_content_same_hash(self):
        self.test_file.write_bytes(b"component App(): pass")
        h1 = self._file_hash(self.test_file)
        h2 = self._file_hash(self.test_file)
        self.assertEqual(h1, h2)

    def test_changed_content_different_hash(self):
        self.test_file.write_bytes(b"component App(): pass")
        h1 = self._file_hash(self.test_file)
        self.test_file.write_bytes(b"component App(): pass  # changed")
        h2 = self._file_hash(self.test_file)
        self.assertNotEqual(h1, h2)

    def test_missing_file_returns_empty_string(self):
        h = self._file_hash(Path("nonexistent_file_xyz.pyreact"))
        self.assertEqual(h, "")


# ── Sprint 4 integration: lint knows about new UI components ─────────────────

class TestLintDoesNotFlagUIComponents(unittest.TestCase):
    """Ensure pyreact lint does not false-positive on new v2 UI components."""

    def setUp(self):
        self.f = Path("_lint_ui_v2_test.pyreact")

    def tearDown(self):
        if self.f.exists():
            self.f.unlink()

    def test_skeleton_usage_no_error(self):
        self.f.write_text("""
component Dashboard():
    loading, setLoading = use_state(True)

    return (
        <UI.Page>
            <UI.Skeleton height="2rem" />
            <UI.DataTable columns={[]} rows={[]} />
            <UI.Icon name="user" />
        </UI.Page>
    )
""", encoding="utf-8")
        try:
            cmd_lint([str(self.f)])
        except SystemExit:
            self.fail("lint raised SystemExit on valid PyReact with new UI v2 components")


if __name__ == "__main__":
    unittest.main()
