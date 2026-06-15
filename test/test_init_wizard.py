import unittest
import shutil
from pathlib import Path
from unittest.mock import patch
from pyreact.cli import cmd_init

class TestInitWizard(unittest.TestCase):
    def setUp(self):
        self.project_path = Path("my-test-wizard-app")
        if self.project_path.exists():
            shutil.rmtree(self.project_path, ignore_errors=True)

    def tearDown(self):
        if self.project_path.exists():
            shutil.rmtree(self.project_path, ignore_errors=True)

    @patch('builtins.input')
    def test_init_wizard_flow(self, mock_input):
        # Mock inputs in order: Project Name, Template choice, Database (y), Auth (y), Routing (y)
        mock_input.side_effect = ["my-test-wizard-app", "2", "y", "y", "y"]
        
        cmd_init([])
        
        # Verify app.pyreact was created
        app_file = self.project_path / "app.pyreact"
        self.assertTrue(app_file.exists())
        
        content = app_file.read_text(encoding="utf-8")
        
        # Since choice is "2" (CRUD) and we enabled db, auth, pages, let's verify:
        # database block is present
        self.assertIn("database {", content)
        # Auth functions in server block
        self.assertIn("def login(", content)
        # Login component
        self.assertIn("component Login():", content)
        # Pages block
        self.assertIn("pages {", content)

        # Check other generated files
        self.assertTrue((self.project_path / "AGENTS.md").exists())
        self.assertTrue((self.project_path / "COOKBOOK.md").exists())
        self.assertTrue((self.project_path / ".cursorrules").exists())
        self.assertTrue((self.project_path / "README.md").exists())
        self.assertTrue((self.project_path / "components" / "Header.pyreact").exists())

if __name__ == '__main__':
    unittest.main()
