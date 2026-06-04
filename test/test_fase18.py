# Test suite for PyReact Fase 18: Real-Time & WebSocket Lanjut
import unittest
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator

class TestFase18(unittest.TestCase):
    def setUp(self):
        self.code = """
        realtime {
            provider = "websockets"
            channels = ["chat", "presence"]
            
            def on_connect(client_id):
                print(f"Client {client_id} connected!")
                broadcast("presence", [client_id])
                
            def on_message(client_id, topic, data):
                print(f"Message from {client_id} on {topic}: {data}")
                
            def on_disconnect(client_id):
                print(f"Client {client_id} disconnected!")
        }
        """

    def test_lexer_realtime_keyword(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        
        # Verify realtime keyword is tokenized
        realtime_token = next((t for t in tokens if t.value == "realtime"), None)
        self.assertIsNotNone(realtime_token)
        from pyreact.compiler.lexer import TT
        self.assertEqual(realtime_token.type, TT.REALTIME)

    def test_parser_realtime_block(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsNotNone(ast.realtime)
        self.assertEqual(ast.realtime.provider, "websockets")
        self.assertEqual(ast.realtime.channels, ["chat", "presence"])
        
        # Verify handlers parsed
        funcs = ast.realtime.functions
        self.assertEqual(len(funcs), 3)
        self.assertEqual(funcs[0].name, "on_connect")
        self.assertEqual(funcs[0].params, ["client_id"])
        self.assertEqual(funcs[1].name, "on_message")
        self.assertEqual(funcs[2].name, "on_disconnect")

    def test_flask_sse_routes_generation(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGenerator(ast, target="flask")
        routes_py = codegen._gen_routes()
        
        # Verify SSE routes and handler wiring
        self.assertIn("@app.route('/api/sse')", routes_py)
        self.assertIn("@app.route('/api/realtime/send', methods=['POST'])", routes_py)
        self.assertIn("realtime_on_connect(client_id)", routes_py)
        self.assertIn("realtime_on_message(client_id, topic, data)", routes_py)
        self.assertIn("realtime_on_disconnect(client_id)", routes_py)

    def test_fastapi_websocket_generation(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        written_files = {}
        def mock_wt(path, content):
            written_files[str(path)] = content
            
        codegen = CodeGenerator(ast, target="fastapi")
        import pyreact.compiler.codegen as cg_mod
        orig_wt = cg_mod.wt
        cg_mod.wt = mock_wt
        try:
            codegen._gen_backend_fastapi()
        finally:
            cg_mod.wt = orig_wt
            
        routes_path = str(codegen.out / "backend" / "routes.py")
        self.assertIn(routes_path, written_files)
        routes_code = written_files[routes_path]
        
        # Verify FastAPI WebSocket setup and handlers wiring
        self.assertIn("@router.websocket(\"/api/ws\")", routes_code)
        self.assertIn("realtime_on_connect(client_id)", routes_code)
        self.assertIn("realtime_on_message(client_id, topic, data)", routes_code)
        self.assertIn("realtime_on_disconnect(client_id)", routes_code)

    def test_api_code_generation(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGenerator(ast, target="flask")
        api_code = codegen._gen_generated_api_code()
        
        # Verify function renaming to avoid namespace collisions
        self.assertIn("def realtime_on_connect(client_id):", api_code)
        self.assertIn("def realtime_on_message(client_id, topic, data):", api_code)
        self.assertIn("def realtime_on_disconnect(client_id):", api_code)

if __name__ == '__main__':
    unittest.main()
