# Test suite for PyReact Fase 27: WebRTC P2P & Audio/Video Streaming
import unittest
import shutil
from pathlib import Path
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator


class TestFase27(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path("test_webrtc_out")
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
    def test_webrtc_block_parses(self):
        """WebRTC block should parse signaling configuration and media codecs."""
        src = """
        webrtc {
            signaling = "websockets"
            codecs = ["vp8", "h264", "opus"]
        }
        component Demo() {
            return (<UI.Page><UI.Text>Hello</UI.Text></UI.Page>)
        }
        """
        tokens = Lexer(src).tokenize()
        tree = Parser(tokens).parse()
        self.assertIsNotNone(tree.webrtc)
        self.assertEqual(tree.webrtc.signaling, "websockets")
        self.assertIn("vp8", tree.webrtc.codecs)
        self.assertIn("opus", tree.webrtc.codecs)

    # ── CodeGen tests ────────────────────────────────────────────────────────
    def test_webrtc_client_js_generated(self):
        """webrtc_client.js must be generated in frontend/src."""
        src = """
        webrtc {
            signaling = "websockets"
        }
        component CallApp() {
            return (<UI.Page><UI.Text>Call</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        client_path = self.out_dir / "frontend" / "src" / "webrtc_client.js"
        self.assertTrue(client_path.exists(), "webrtc_client.js was not generated")
        content = client_path.read_text(encoding="utf-8")
        self.assertIn("useWebRTC", content)
        self.assertIn("RTCPeerConnection", content)

    def test_webrtc_components_jsx_generated(self):
        """webrtc_components.jsx must be generated inside frontend/src/ui/."""
        src = """
        webrtc {
            signaling = "websockets"
        }
        component AudioRoomApp() {
            return (<UI.Page><UI.Text>Audio Room</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        components_path = self.out_dir / "frontend" / "src" / "ui" / "webrtc_components.jsx"
        self.assertTrue(components_path.exists(), "webrtc_components.jsx was not generated")
        content = components_path.read_text(encoding="utf-8")
        self.assertIn("VideoCall", content)
        self.assertIn("AudioRoom", content)
        self.assertIn("useWebRTC", content)

    def test_webrtc_signaling_py_generated_when_backend_exists(self):
        """webrtc_signaling.py must be generated in backend/ and patch routes.py."""
        src = """
        server {
            def call_log():
                return {"logs": []}
        }
        webrtc {
            signaling = "websockets"
            codecs = ["vp8", "opus"]
        }
        component App() {
            return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        sig_path = self.out_dir / "backend" / "webrtc_signaling.py"
        self.assertTrue(sig_path.exists(), "webrtc_signaling.py was not generated")
        
        # Verify routes.py has registered the webrtc blueprint
        routes_path = self.out_dir / "backend" / "routes.py"
        self.assertTrue(routes_path.exists())
        routes_txt = routes_path.read_text(encoding="utf-8")
        self.assertIn("webrtc_bp", routes_txt)
        self.assertIn("webrtc_signaling", routes_txt)


if __name__ == "__main__":
    unittest.main()
