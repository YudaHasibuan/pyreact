# Test suite for PyReact Fase 19: Testing Framework Terpadu
import unittest
from pathlib import Path
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.tester import generate_backend_tests, render_jsx_to_mock_html, generate_e2e_tests

class TestFase19(unittest.TestCase):
    def setUp(self):
        self.code = """
        server {
            def add_user(username: String, points: Number, active: Boolean) -> String:
                return f"Added {username}"
        }
        
        component UserCard():
            name, setName = use_state("John Doe")
            return (
                <UI.Card>
                    <UI.Heading>{name}</UI.Heading>
                    <UI.Button onClick={() => console.log("clicked")}>Click Me</UI.Button>
                </UI.Card>
            )
        """

    def test_backend_test_generation(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Test Flask generation
        test_py = generate_backend_tests(ast, "flask")
        self.assertIn("class TestBackendGenerated(unittest.TestCase):", test_py)
        self.assertIn("def test_add_user_valid(self):", test_py)
        self.assertIn("def test_add_user_invalid_type(self):", test_py)
        self.assertIn("self.assertEqual(res.status_code, 200)", test_py)
        
        # Verify valid/invalid payload values injected correctly
        self.assertIn("'username': 'test_string'", test_py)
        self.assertIn("'points': 'not_a_number'", test_py)
        self.assertIn("'active': True", test_py)

    def test_jsx_snapshot_rendering(self):
        lexer = Lexer(self.code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        comp = ast.components[0]
        mock_html = render_jsx_to_mock_html(comp.jsx, comp.states)
        
        # Verify component structures cleaned
        self.assertNotIn("<UI.Card>", mock_html)
        self.assertIn("<Card>", mock_html)
        # Verify states placeholder replaced with initial value
        self.assertIn("<Heading>John Doe</Heading>", mock_html)
        # Verify event listener cleaned
        self.assertIn('onclick="mock_handler()"', mock_html)

    def test_e2e_playwright_test_code(self):
        e2e_code = generate_e2e_tests("flask")
        self.assertIn("def test_e2e_homepage_load():", e2e_code)
        self.assertIn("from playwright.sync_api import sync_playwright", e2e_code)

if __name__ == '__main__':
    unittest.main()
