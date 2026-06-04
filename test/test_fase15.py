# Test suite for PyReact Fase 15: Pydantic Validation & TypeScript Declarations
import unittest
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator

class TestFase15(unittest.TestCase):
    def setUp(self):
        self.code = """
        server {
            def process_user(username: String, age: Optional[Number], is_active: Boolean) -> String:
                return f"User {username} (age: {age}) active status is {is_active}"
        }
        """

    def test_parser_type_annotations(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsNotNone(ast.server)
        self.assertEqual(len(ast.server.functions), 1)
        f = ast.server.functions[0]
        self.assertEqual(f.name, "process_user")
        self.assertEqual(f.param_types.get("username"), "String")
        self.assertEqual(f.param_types.get("age"), "Optional[Number]")
        self.assertEqual(f.param_types.get("is_active"), "Boolean")
        self.assertEqual(f.return_type, "String")

    def test_pydantic_schemas_and_flask_routes(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGenerator(ast, target="flask")
        routes_py = codegen._gen_routes()
        
        # Verify Pydantic schema generation
        self.assertIn("class Schema_process_user(BaseModel):", routes_py)
        self.assertIn("username: str", routes_py)
        self.assertIn("age: Optional[float] = None", routes_py)
        self.assertIn("is_active: bool", routes_py)
        
        # Verify validation call and error handling
        self.assertIn("Schema_process_user.model_validate(payload)", routes_py)
        self.assertIn("except ValidationError as val_err:", routes_py)

    def test_fastapi_routes_validation(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # We need to run _gen_backend_fastapi to verify route code since routes_code is constructed there
        # Let's mock a writer for wt so we can capture routes.py content without writing to disk
        written_files = {}
        def mock_wt(path, content):
            written_files[str(path)] = content
            
        codegen = CodeGenerator(ast, target="flask")
        # override wt
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
        
        # Verify pydantic schema is present
        self.assertIn("class Schema_process_user(BaseModel):", routes_code)
        # Verify route uses model_validate
        self.assertIn("Schema_process_user.model_validate(payload)", routes_code)
        self.assertIn("except ValidationError as val_err:", routes_code)

    def test_ts_declarations(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGenerator(ast, target="flask")
        ts_code = codegen._gen_ts_declarations()
        
        # Verify TS Interface structure
        self.assertIn("export interface ServerBridge {", ts_code)
        self.assertIn("process_user(payload: { username: string; age?: number | null; is_active: boolean }): Promise<string>;", ts_code)
        self.assertIn("export const server: ServerBridge;", ts_code)

if __name__ == '__main__':
    unittest.main()
