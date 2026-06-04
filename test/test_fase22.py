# Test suite for PyReact Fase 22: Server-Side Rendering (SSR) Hybrid
import unittest
import shutil
import sys
import os
from pathlib import Path
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator

class TestFase22(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path("test_ssr_out")
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)
        self.out_dir.mkdir(exist_ok=True)

    def tearDown(self):
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)

    def test_ssr_generation(self):
        sample_code = """
        component Header(title) {
            return (
                <UI.Navbar title={title}>
                    <div className="flex gap-4">
                        <UI.Text>Links</UI.Text>
                    </div>
                </UI.Navbar>
            )
        }

        component Home() {
            return (
                <UI.Page>
                    <Header title="My PyReact Site" />
                    <UI.Card title="Welcome Home">
                        <UI.Text>Welcome to the pre-rendered SSR experience!</UI.Text>
                    </UI.Card>
                </UI.Page>
            )
        }
        """
        
        lexer = Lexer(sample_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast.components), 2)
        
        # Generate code
        codegen = CodeGenerator(ast, out_dir=self.out_dir)
        codegen.generate()
        
        # Verify ssr.py was created
        ssr_path = self.out_dir / "backend" / "ssr.py"
        self.assertTrue(ssr_path.exists())
        
        ssr_code = ssr_path.read_text(encoding="utf-8")
        self.assertIn("def render_Header", ssr_code)
        self.assertIn("def render_Home", ssr_code)
        self.assertIn("render_Header(title=\"My PyReact Site\")", ssr_code)
        
        # Verify routes.py was created and contains ssr_root
        routes_path = self.out_dir / "backend" / "routes.py"
        self.assertTrue(routes_path.exists())
        routes_code = routes_path.read_text(encoding="utf-8")
        self.assertIn("def ssr_root():", routes_code)
        self.assertIn("ssr.render_component('Home')", routes_code)

if __name__ == '__main__':
    unittest.main()
