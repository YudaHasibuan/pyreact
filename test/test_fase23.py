# Test suite for PyReact Fase 23: Offline-First PWA & Background Sync
import unittest
import shutil
from pathlib import Path
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator

class TestFase23(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path("test_pwa_out")
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)
        self.out_dir.mkdir(exist_ok=True)

    def tearDown(self):
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)

    def test_pwa_generation(self):
        sample_code = """
        shared_state {
            counter = 0
            username = "guest"
        }

        component Home() {
            return (
                <UI.Page>
                    <UI.NetworkStatus />
                    <UI.Card title="PWA Home">
                        <UI.Text>PWA ready</UI.Text>
                    </UI.Card>
                </UI.Page>
            )
        }
        """
        
        lexer = Lexer(sample_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGenerator(ast, out_dir=self.out_dir)
        codegen.generate()
        
        # Verify public files were generated
        public_dir = self.out_dir / "frontend" / "public"
        self.assertTrue((public_dir / "manifest.json").exists())
        self.assertTrue((public_dir / "sw.js").exists())
        
        # Verify INDEX_HTML updated
        index_html = (self.out_dir / "frontend" / "index.html").read_text(encoding="utf-8")
        self.assertIn('link rel="manifest"', index_html)
        
        # Verify MAIN_JSX registered service worker
        main_jsx = (self.out_dir / "frontend" / "src" / "main.jsx").read_text(encoding="utf-8")
        self.assertIn("serviceWorker", main_jsx)

        # Verify components.jsx has NetworkStatus
        components_jsx = (self.out_dir / "frontend" / "src" / "ui" / "components.jsx").read_text(encoding="utf-8")
        self.assertIn("NetworkStatus", components_jsx)
        self.assertIn("isOnline", components_jsx)

        # Verify pybridge.js has offline queueing
        pybridge_js = (self.out_dir / "frontend" / "src" / "pybridge.js").read_text(encoding="utf-8")
        self.assertIn("pyreact_offline_queue", pybridge_js)
        self.assertIn("navigator.onLine", pybridge_js)
        self.assertIn('window.addEventListener("online"', pybridge_js)

        # Verify store.js has local state caching
        store_js = (self.out_dir / "frontend" / "src" / "store.js").read_text(encoding="utf-8")
        self.assertIn("pyreact_shared_state", store_js)
        self.assertIn("localStorage.setItem", store_js)
        self.assertIn("defaultState", store_js)

if __name__ == '__main__':
    unittest.main()
