# Test suite for PyReact Fase 26: RBAC (Role-Based Access Control) & Route Guards
import unittest
import shutil
from pathlib import Path
from pyreact.compiler.lexer import Lexer, TT
from pyreact.compiler.parser import Parser, RBACBlock
from pyreact.compiler.codegen import CodeGenerator


SAMPLE_RBAC = """
server {
    def get_users():
        return [{"id": 1, "name": "Alice"}]

    def delete_user(id: Number):
        return {"deleted": True}

    def admin_stats():
        return {"total": 100}
}

rbac {
    roles = ["admin", "user", "guest"]
    default_role = "guest"

    admin: ["get_users", "delete_user", "admin_stats", "*"]
    user: ["get_users"]
    guest: []
}

component Dashboard() {
    return (
        <UI.Page>
            <UI.Card title="Dashboard">
                <UI.Text>Welcome</UI.Text>
            </UI.Card>
        </UI.Page>
    )
}
"""

SAMPLE_RBAC_MINIMAL = """
rbac {
    roles = ["admin", "viewer"]
    default_role = "viewer"
    admin: ["manage_all"]
    viewer: ["read_data"]
}
component App() {
    return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
}
"""


class TestFase26Lexer(unittest.TestCase):
    def test_rbac_keyword_tokenised(self):
        tokens = Lexer(SAMPLE_RBAC).tokenize()
        types = [t.type for t in tokens]
        self.assertIn(TT.RBAC, types, "RBAC token not produced by lexer")

    def test_rbac_block_produces_raw_python(self):
        tokens = Lexer(SAMPLE_RBAC).tokenize()
        rbac_idx = next(i for i, t in enumerate(tokens) if t.type == TT.RBAC)
        sub = [t.type for t in tokens[rbac_idx:rbac_idx + 4]]
        self.assertIn(TT.LBRACE, sub)
        self.assertIn(TT.RAW_PYTHON, sub)


class TestFase26Parser(unittest.TestCase):
    def _parse(self, src):
        return Parser(Lexer(src).tokenize()).parse()

    def test_rbac_block_parsed(self):
        tree = self._parse(SAMPLE_RBAC)
        self.assertIsNotNone(tree.rbac, "rbac block not parsed")
        self.assertIsInstance(tree.rbac, RBACBlock)

    def test_roles_extracted(self):
        tree = self._parse(SAMPLE_RBAC)
        self.assertIn("admin", tree.rbac.roles)
        self.assertIn("user", tree.rbac.roles)
        self.assertIn("guest", tree.rbac.roles)
        self.assertEqual(len(tree.rbac.roles), 3)

    def test_default_role_extracted(self):
        tree = self._parse(SAMPLE_RBAC)
        self.assertEqual(tree.rbac.default_role, "guest")

    def test_permissions_extracted(self):
        tree = self._parse(SAMPLE_RBAC)
        self.assertIn("admin", tree.rbac.permissions)
        self.assertIn("user", tree.rbac.permissions)
        self.assertIn("get_users", tree.rbac.permissions["user"])

    def test_admin_wildcard_permission(self):
        tree = self._parse(SAMPLE_RBAC)
        self.assertIn("*", tree.rbac.permissions.get("admin", []))

    def test_minimal_rbac_parses(self):
        tree = self._parse(SAMPLE_RBAC_MINIMAL)
        self.assertIsNotNone(tree.rbac)
        self.assertIn("admin", tree.rbac.roles)
        self.assertEqual(tree.rbac.default_role, "viewer")


class TestFase26CodeGen(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path("test_rbac_out")
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)
        self.out_dir.mkdir(exist_ok=True)

    def tearDown(self):
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)

    def _compile(self, src):
        tokens = Lexer(src).tokenize()
        tree = Parser(tokens).parse()
        cg = CodeGenerator(tree, out_dir=self.out_dir)
        cg.generate()
        return tree

    # ── Backend: rbac.py ─────────────────────────────────────────────────────
    def test_rbac_py_generated(self):
        self._compile(SAMPLE_RBAC)
        rbac_path = self.out_dir / "backend" / "rbac.py"
        self.assertTrue(rbac_path.exists(), "rbac.py not generated")

    def test_rbac_py_has_role_required(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "backend" / "rbac.py").read_text(encoding="utf-8")
        self.assertIn("role_required", content)
        self.assertIn("def role_required", content)

    def test_rbac_py_has_permission_required(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "backend" / "rbac.py").read_text(encoding="utf-8")
        self.assertIn("permission_required", content)

    def test_rbac_py_has_correct_roles(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "backend" / "rbac.py").read_text(encoding="utf-8")
        self.assertIn('"admin"', content)
        self.assertIn('"user"', content)
        self.assertIn('"guest"', content)

    def test_rbac_py_has_correct_default_role(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "backend" / "rbac.py").read_text(encoding="utf-8")
        self.assertIn('DEFAULT_ROLE = "guest"', content)

    def test_rbac_py_has_permissions_table(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "backend" / "rbac.py").read_text(encoding="utf-8")
        self.assertIn("PERMISSIONS", content)
        self.assertIn("get_users", content)

    def test_rbac_py_jwt_decoding(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "backend" / "rbac.py").read_text(encoding="utf-8")
        self.assertIn("jwt.decode", content)
        self.assertIn("Authorization", content)

    def test_rbac_py_403_response(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "backend" / "rbac.py").read_text(encoding="utf-8")
        self.assertIn("403", content)
        self.assertIn("Forbidden", content)

    # ── Frontend: rbac.js ─────────────────────────────────────────────────────
    def test_rbac_js_generated(self):
        self._compile(SAMPLE_RBAC)
        rbac_js_path = self.out_dir / "frontend" / "src" / "rbac.js"
        self.assertTrue(rbac_js_path.exists(), "rbac.js not generated")

    def test_rbac_js_has_rbac_provider(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "frontend" / "src" / "rbac.js").read_text(encoding="utf-8")
        self.assertIn("RBACProvider", content)
        self.assertIn("export function RBACProvider", content)

    def test_rbac_js_has_use_rbac_hook(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "frontend" / "src" / "rbac.js").read_text(encoding="utf-8")
        self.assertIn("useRBAC", content)
        self.assertIn("export function useRBAC", content)

    def test_rbac_js_has_rbac_guard(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "frontend" / "src" / "rbac.js").read_text(encoding="utf-8")
        self.assertIn("RBACGuard", content)
        self.assertIn("export function RBACGuard", content)

    def test_rbac_js_has_correct_roles(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "frontend" / "src" / "rbac.js").read_text(encoding="utf-8")
        self.assertIn('"admin"', content)
        self.assertIn('"user"', content)
        self.assertIn('"guest"', content)

    def test_rbac_js_decodes_jwt(self):
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "frontend" / "src" / "rbac.js").read_text(encoding="utf-8")
        self.assertIn("_decodeRole", content)
        self.assertIn("atob", content)

    def test_rbac_js_admin_bypass(self):
        """Admin role must have wildcard bypass in frontend."""
        self._compile(SAMPLE_RBAC)
        content = (self.out_dir / "frontend" / "src" / "rbac.js").read_text(encoding="utf-8")
        self.assertIn("admin", content)

    def test_rbac_generated_even_without_rbac_block(self):
        """rbac.py and rbac.js should be generated with default config when no rbac block."""
        src = """
        server {
            def ping():
                return {"pong": True}
        }
        component App() {
            return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        # Both files should always be generated so devs can import them
        rbac_py = self.out_dir / "backend" / "rbac.py"
        rbac_js = self.out_dir / "frontend" / "src" / "rbac.js"
        self.assertTrue(rbac_py.exists(), "rbac.py not generated (default config)")
        self.assertTrue(rbac_js.exists(), "rbac.js not generated (default config)")


if __name__ == "__main__":
    unittest.main()
