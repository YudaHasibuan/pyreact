# Test suite for PyReact Fase 14: Automated Database Migrations & Admin Panel
import unittest
from pyreact.compiler.lexer import Lexer, TT
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator

class TestFase14(unittest.TestCase):
    def setUp(self):
        self.code = """
        database {
            provider = "sqlite"
            url = "test.sqlite"
        }
        
        server {
            class DbUser(db.Model):
                id = db.Column(db.Integer, primary_key=True)
                username = db.Column(db.String(50), unique=True)
                email = db.Column(db.String(100), nullable=True)
        }
        """

    def test_database_parser(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertIsNotNone(ast.database)
        self.assertEqual(ast.database.provider, "sqlite")
        self.assertEqual(ast.database.url, "test.sqlite")

    def test_flask_auto_migration_generation(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGenerator(ast, target="flask")
        routes_py = codegen._gen_routes()
        app_py = codegen._gen_backend()
        
        # Verify routes contain admin routes
        self.assertIn("/api/admin/tables", routes_py)
        self.assertIn("/api/admin/table/<table_name>", routes_py)
        self.assertIn("/api/admin/table/<table_name>/<pk_val>", routes_py)
        
        # Verify app.py contains ALTER TABLE auto-migration logic
        self.assertIn("ALTER TABLE", app_py)

    def test_app_jsx_conditional_admin_console(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGenerator(ast, target="flask")
        app_jsx = codegen._gen_app_jsx()
        
        # Verify conditional lazy importing and rendering of AdminConsole
        self.assertIn("const AdminConsole = React.lazy(() => import(\"./ui/Admin\"));", app_jsx)
        self.assertIn("window.location.pathname === '/admin'", app_jsx)
        self.assertIn("isAdmin ? (", app_jsx)
        self.assertIn("<AdminConsole />", app_jsx)

    def test_admin_jsx_gorgeous_design(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGenerator(ast, target="flask")
        admin_jsx = codegen._gen_admin_jsx()
        
        # Verify the structure and premium UI styles in generated Admin.jsx
        self.assertIn("export default function AdminConsole()", admin_jsx)
        self.assertIn("PyReact Admin Console", admin_jsx)
        self.assertIn("bg-[#070b13]", admin_jsx)
        self.assertIn("backdrop-blur-xl", admin_jsx)
        self.assertIn("Add Record", admin_jsx)

if __name__ == '__main__':
    unittest.main()
