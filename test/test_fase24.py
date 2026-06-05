# Test suite for PyReact Fase 24: Real-time Collaborative State (CRDT-lite)
import unittest
import shutil
from pathlib import Path
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator


class TestFase24(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path("test_crdt_out")
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)
        self.out_dir.mkdir(exist_ok=True)

    def tearDown(self):
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)

    # ── helper ────────────────────────────────────────────────────────────────
    def _compile(self, src: str):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        cg = CodeGenerator(ast, out_dir=self.out_dir)
        cg.generate()
        return ast

    # ── Lexer / Parser tests ─────────────────────────────────────────────────
    def test_realtime_block_still_parses(self):
        """Existing realtime block should still parse correctly."""
        src = """
        realtime {
            provider = "websockets"
            channels = ["collab", "presence"]
        }
        component Demo() {
            return (<UI.Page><UI.Text>Hello</UI.Text></UI.Page>)
        }
        """
        tokens = Lexer(src).tokenize()
        tree = Parser(tokens).parse()
        self.assertIsNotNone(tree.realtime)
        self.assertEqual(tree.realtime.provider, "websockets")
        self.assertIn("collab", tree.realtime.channels)

    # ── CodeGen tests ────────────────────────────────────────────────────────
    def test_crdt_js_generated(self):
        """crdt.js must always be generated in frontend/src."""
        src = """
        component Collab() {
            return (<UI.Page><UI.Text>Collaborative</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        crdt_path = self.out_dir / "frontend" / "src" / "crdt.js"
        self.assertTrue(crdt_path.exists(), "crdt.js was not generated")

    def test_crdt_js_has_vector_clock(self):
        """crdt.js must contain the vector clock implementation."""
        src = """
        component Whiteboard() {
            return (<UI.Page><UI.Text>Whiteboard</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        content = (self.out_dir / "frontend" / "src" / "crdt.js").read_text(encoding="utf-8")
        self.assertIn("tickClock", content)
        self.assertIn("mergeClock", content)
        self.assertIn("clockAfter", content)

    def test_crdt_js_has_crdt_document(self):
        """crdt.js must contain the CRDTDocument class."""
        src = """
        component Editor() {
            return (<UI.Page><UI.Text>Editor</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        content = (self.out_dir / "frontend" / "src" / "crdt.js").read_text(encoding="utf-8")
        self.assertIn("CRDTDocument", content)
        self.assertIn("LWW", content.upper().replace("-", ""))  # LWW mention

    def test_crdt_js_has_use_realtime_channel_hook(self):
        """crdt.js must export useRealtimeChannel hook."""
        src = """
        component Presence() {
            return (<UI.Page><UI.Text>Presence</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        content = (self.out_dir / "frontend" / "src" / "crdt.js").read_text(encoding="utf-8")
        self.assertIn("useRealtimeChannel", content)
        self.assertIn("export function useRealtimeChannel", content)

    def test_crdt_js_has_websocket_transport(self):
        """crdt.js must manage WebSocket for CRDT op broadcasting."""
        src = """
        component Live() {
            return (<UI.Page><UI.Text>Live</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        content = (self.out_dir / "frontend" / "src" / "crdt.js").read_text(encoding="utf-8")
        self.assertIn("ensureWS", content)
        self.assertIn("__crdt", content)
        self.assertIn("wsSend", content)

    def test_crdt_broadcast_py_generated_when_backend_exists(self):
        """crdt_broadcast.py helper must be generated in dist/backend."""
        src = """
        server {
            def ping():
                return {"msg": "pong"}
        }
        component App() {
            return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        be_path = self.out_dir / "backend" / "crdt_broadcast.py"
        self.assertTrue(be_path.exists(), "crdt_broadcast.py was not generated")
        content = be_path.read_text(encoding="utf-8")
        self.assertIn("broadcast_crdt", content)
        self.assertIn("__crdt", content)

    def test_crdt_node_id_unique_per_client(self):
        """crdt.js must generate unique node IDs per browser tab."""
        src = """
        component App() {
            return (<UI.Page><UI.Text>A</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        content = (self.out_dir / "frontend" / "src" / "crdt.js").read_text(encoding="utf-8")
        self.assertIn("Math.random", content)
        self.assertIn("_nodeId", content)

    def test_crdt_merge_conflict_resolution(self):
        """CRDTDocument merge method must exist and handle conflicts."""
        src = """
        component App() {
            return (<UI.Page><UI.Text>A</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        content = (self.out_dir / "frontend" / "src" / "crdt.js").read_text(encoding="utf-8")
        self.assertIn("merge(op)", content)
        self.assertIn("clockAfter", content)


if __name__ == "__main__":
    unittest.main()
