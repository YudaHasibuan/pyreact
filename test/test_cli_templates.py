# Test suite for PyReact CLI Templates selection
import unittest
import shutil
from pathlib import Path
from pyreact.cli import cmd_new


class TestCLITemplates(unittest.TestCase):
    def setUp(self):
        self.dirs = [
            Path("my-test-app"),
            Path("my-test-app-graphql"),
            Path("my-test-app-rbac"),
            Path("my-test-app-webrtc"),
            Path("my-test-app-crud"),
            Path("my-test-app-dashboard")
        ]
        for d in self.dirs:
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)

    def tearDown(self):
        for d in self.dirs:
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)

    def test_new_with_collab_template(self):
        """new command with collab template argument should scaffold collab app code."""
        cmd_new(["my-test-app", "--template", "collab"])
        app_file = Path("my-test-app") / "app.pyreact"
        self.assertTrue(app_file.exists())
        content = app_file.read_text(encoding="utf-8")
        self.assertIn("realtime {", content)

    def test_new_with_graphql_template(self):
        """new command with graphql template argument should scaffold graphql app code."""
        cmd_new(["my-test-app-graphql", "--template", "graphql"])
        app_file = Path("my-test-app-graphql") / "app.pyreact"
        self.assertTrue(app_file.exists())
        content = app_file.read_text(encoding="utf-8")
        self.assertIn("graphql {", content)

    def test_new_with_rbac_template(self):
        """new command with rbac template argument should scaffold rbac app code."""
        cmd_new(["my-test-app-rbac", "--template", "rbac"])
        app_file = Path("my-test-app-rbac") / "app.pyreact"
        self.assertTrue(app_file.exists())
        content = app_file.read_text(encoding="utf-8")
        self.assertIn("rbac {", content)

    def test_new_with_webrtc_template(self):
        """new command with webrtc template argument should scaffold webrtc app code."""
        cmd_new(["my-test-app-webrtc", "--template", "webrtc"])
        app_file = Path("my-test-app-webrtc") / "app.pyreact"
        self.assertTrue(app_file.exists())
        content = app_file.read_text(encoding="utf-8")
        self.assertIn("webrtc {", content)

    def test_new_with_crud_template(self):
        """new command with crud template argument should scaffold CRUD app code."""
        cmd_new(["my-test-app-crud", "--template", "crud"])
        app_file = Path("my-test-app-crud") / "app.pyreact"
        self.assertTrue(app_file.exists())
        content = app_file.read_text(encoding="utf-8")
        self.assertIn("DbTask", content)
        self.assertIn("get_tasks", content)

    def test_new_with_dashboard_template(self):
        """new command with dashboard template argument should scaffold dashboard app code."""
        cmd_new(["my-test-app-dashboard", "--template", "dashboard"])
        app_file = Path("my-test-app-dashboard") / "app.pyreact"
        self.assertTrue(app_file.exists())
        content = app_file.read_text(encoding="utf-8")
        self.assertIn("get_stats", content)
        self.assertIn("Analytics Dashboard", content)


if __name__ == "__main__":
    unittest.main()
