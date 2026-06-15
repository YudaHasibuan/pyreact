# Test suite for PyReact Fase 29: Interactive pyreact init Wizard & Rich Scaffolding
import unittest
import shutil
from pathlib import Path
from unittest.mock import patch
from pyreact.cli import _customize_scaffold_code, cmd_init, SCAFFOLD_APP


class TestFase29(unittest.TestCase):
    def setUp(self):
        self.test_project_dir = Path("my-test-wizard-app")
        if self.test_project_dir.exists():
            shutil.rmtree(self.test_project_dir, ignore_errors=True)

    def tearDown(self):
        if self.test_project_dir.exists():
            shutil.rmtree(self.test_project_dir, ignore_errors=True)

    def test_customize_scaffold_code_db_only(self):
        """Should add database block and SQLite model if enable_db is True."""
        custom_code = _customize_scaffold_code(SCAFFOLD_APP, enable_db=True, enable_auth=False, enable_pages=False)
        self.assertIn("database {", custom_code)
        self.assertIn("provider = \"sqlite\"", custom_code)
        self.assertIn("class DbItem(db.Model):", custom_code)

    def test_customize_scaffold_code_auth_only(self):
        """Should add JWT dependencies, login/get_profile endpoints, and Login/Dashboard components."""
        custom_code = _customize_scaffold_code(SCAFFOLD_APP, enable_db=False, enable_auth=True, enable_pages=False)
        self.assertIn("dependencies {", custom_code)
        self.assertIn("\"PyJWT\"", custom_code)
        self.assertIn("def login(username, password):", custom_code)
        self.assertIn("def get_profile():", custom_code)
        self.assertIn("component Login():", custom_code)
        self.assertIn("component Dashboard():", custom_code)

    def test_customize_scaffold_code_pages_only(self):
        """Should add pages block configuration if enable_pages is True."""
        custom_code = _customize_scaffold_code(SCAFFOLD_APP, enable_db=False, enable_auth=False, enable_pages=True)
        self.assertIn("pages {", custom_code)
        self.assertIn("Home      = \"/\"", custom_code)

    def test_cmd_init_creates_project_files(self):
        """cmd_init should generate the correct boilerplate files based on user prompts."""
        inputs = [
            "my-test-wizard-app",  # Project Name
            "1",                    # Standard Fullstack App
            "y",                    # Enable DB
            "y",                    # Enable Auth
            "y",                    # Enable Pages
        ]
        
        with patch('builtins.input', side_effect=inputs):
            cmd_init([])
            
        self.assertTrue(self.test_project_dir.exists())
        self.assertTrue((self.test_project_dir / "app.pyreact").exists())
        self.assertTrue((self.test_project_dir / "README.md").exists())
        self.assertTrue((self.test_project_dir / "AGENTS.md").exists())
        self.assertTrue((self.test_project_dir / "COOKBOOK.md").exists())
        self.assertTrue((self.test_project_dir / ".cursorrules").exists())
        self.assertTrue((self.test_project_dir / "components" / "Header.pyreact").exists())
        
        # Verify customized content inside generated app.pyreact
        app_content = (self.test_project_dir / "app.pyreact").read_text(encoding="utf-8")
        self.assertIn("database {", app_content)
        self.assertIn("dependencies {", app_content)
        self.assertIn("pages {", app_content)
        self.assertIn("component Login():", app_content)
        self.assertIn("component Dashboard():", app_content)

    def test_init_hub_template_generates_context_files(self):
        """init_hub_template should copy context files (AGENTS.md, COOKBOOK.md, etc.) and create components dir."""
        from pyreact.compiler.ppr import init_hub_template
        
        success = init_hub_template("saas", self.test_project_dir)
        self.assertTrue(success)
        
        self.assertTrue(self.test_project_dir.exists())
        self.assertTrue((self.test_project_dir / "app.pyreact").exists())
        self.assertTrue((self.test_project_dir / "README.md").exists())
        self.assertTrue((self.test_project_dir / "AGENTS.md").exists())
        self.assertTrue((self.test_project_dir / "COOKBOOK.md").exists())
        self.assertTrue((self.test_project_dir / ".cursorrules").exists())
        self.assertTrue((self.test_project_dir / "components" / "Header.pyreact").exists())


if __name__ == "__main__":
    unittest.main()
