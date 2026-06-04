# Test suite for PyReact Fase 13: WebAssembly (WASM) & Edge Compilation.
import unittest
from pathlib import Path
import shutil
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator, PyToJsTranspiler

class TestFase13(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_output_fase13")
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_transpiler_function_def(self):
        # Verify that Python function definition compiles correctly to JS
        py_source = "def add(a, b):\n    return a + b\n"
        transpiler = PyToJsTranspiler()
        js_code = transpiler.transpile(py_source)
        self.assertIn("async function add(a, b)", js_code)
        self.assertIn("return (a + b);", js_code)

    def test_wasm_compilation(self):
        # Verify WASM compilation outputs index.html with Pyodide and generated_api.py
        code = """
        server {
            def greeting(name):
                return "Hello " + name
        }
        """
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        codegen = CodeGenerator(ast, out_dir=str(self.test_dir), target="wasm")
        codegen.generate()

        wasm_path = self.test_dir / "wasm"
        self.assertTrue((wasm_path / "index.html").exists())
        self.assertTrue((wasm_path / "generated_api.py").exists())
        
        index_content = (wasm_path / "index.html").read_text(encoding="utf-8")
        self.assertIn("window.__pyreact_wasm__ = true", index_content)
        self.assertIn("loadPyodide()", index_content)
        
        api_content = (wasm_path / "generated_api.py").read_text(encoding="utf-8")
        self.assertIn("def greeting(name):", api_content)

    def test_edge_compilation(self):
        # Verify Edge worker output wrangler.toml and transpiled worker.js
        code = """
        server {
            def multiply(x, y):
                return x * y
        }
        """
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        codegen = CodeGenerator(ast, out_dir=str(self.test_dir), target="edge")
        codegen.generate()

        edge_path = self.test_dir / "edge"
        self.assertTrue((edge_path / "wrangler.toml").exists())
        self.assertTrue((edge_path / "worker.js").exists())
        
        worker_content = (edge_path / "worker.js").read_text(encoding="utf-8")
        self.assertIn("async function multiply(x, y)", worker_content)
        self.assertIn("endpoint === \"multiply\"", worker_content)

if __name__ == '__main__':
    unittest.main()
