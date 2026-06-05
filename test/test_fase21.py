# Test suite for PyReact Fase 21: PyReact Cloud
import unittest
import json
import shutil
import os
from pathlib import Path
from pyreact.cli import cmd_secrets, cmd_domain, cmd_deploy

class TestFase21(unittest.TestCase):
    def setUp(self):
        # Setup clean test files
        self.secrets_file = Path(".pyreact_secrets.json")
        self.domains_file = Path(".pyreact_domains.json")
        self.dist_dir = Path("dist")
        
        if self.secrets_file.exists(): self.secrets_file.unlink()
        if self.domains_file.exists(): self.domains_file.unlink()
        if self.dist_dir.exists(): shutil.rmtree(self.dist_dir, ignore_errors=True)
        self.dist_dir.mkdir(exist_ok=True)
        (self.dist_dir / "backend").mkdir(exist_ok=True)
        (self.dist_dir / "backend" / "app.py").touch()

    def tearDown(self):
        # Cleanup
        if self.secrets_file.exists(): self.secrets_file.unlink()
        if self.domains_file.exists(): self.domains_file.unlink()
        if self.dist_dir.exists(): shutil.rmtree(self.dist_dir, ignore_errors=True)

    def test_secrets_management(self):
        # Set a secret key
        cmd_secrets(["set", "API_KEY", "secret12345"])
        self.assertTrue(self.secrets_file.exists())
        
        with open(self.secrets_file, "r") as f:
            data = json.load(f)
        self.assertEqual(data.get("API_KEY"), "secret12345")
        
        # Test listing secrets doesn't crash
        cmd_secrets(["list"])
        
        # Remove a secret key
        cmd_secrets(["remove", "API_KEY"])
        with open(self.secrets_file, "r") as f:
            data = json.load(f)
        self.assertNotIn("API_KEY", data)

    def test_domain_management(self):
        # Add custom domain
        cmd_domain(["add", "mycustomdomain.com"])
        self.assertTrue(self.domains_file.exists())
        
        with open(self.domains_file, "r") as f:
            data = json.load(f)
        self.assertIn("mycustomdomain.com", data)
        
        # List domains
        cmd_domain(["list"])
        
        # Remove custom domain
        cmd_domain(["remove", "mycustomdomain.com"])
        with open(self.domains_file, "r") as f:
            data = json.load(f)
        self.assertNotIn("mycustomdomain.com", data)

    def test_cloud_deployment(self):
        # Preconfigure secret and domain
        cmd_secrets(["set", "DATABASE_URL", "postgres://localhost/db"])
        cmd_domain(["add", "app.coolsite.org"])
        
        # Perform deployment
        cmd_deploy([])
        
        # Verify zip archive created
        zip_path = self.dist_dir / "deployment.zip"
        self.assertTrue(zip_path.exists())
        self.assertGreater(zip_path.stat().st_size, 0)
        
        # Verify deploy metadata exists and holds correct config
        meta_path = self.dist_dir / "deploy_meta.json"
        self.assertTrue(meta_path.exists())
        with open(meta_path, "r") as f:
            meta = json.load(f)
        self.assertEqual(meta.get("secrets_count"), 1)
        self.assertIn("app.coolsite.org", meta.get("custom_domains"))
        self.assertIn("pyreact.app", meta.get("url"))

        # Verify live monitoring local dashboard generated
        dashboard_path = self.dist_dir / "dashboard.html"
        self.assertTrue(dashboard_path.exists())
        dashboard_content = dashboard_path.read_text(encoding="utf-8")
        self.assertIn("PyReact Cloud Dashboard", dashboard_content)
        self.assertIn("app.coolsite.org", dashboard_content)
        self.assertIn("DATABASE_URL", dashboard_content)

    def test_cli_help_options(self):
        import sys
        from io import StringIO
        from pyreact.cli import main
        
        # Test help options
        for help_arg in ["-h", "--help", "-help", "help"]:
            sys.argv = ["pyreact", help_arg]
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            try:
                main()
                output = sys.stdout.getvalue()
                self.assertIn("Usage: pyreact <command> [options]", output)
            finally:
                sys.stdout = old_stdout

if __name__ == '__main__':
    unittest.main()
