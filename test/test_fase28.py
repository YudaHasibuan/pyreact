# Test suite for PyReact Fase 28: Multi-Database Support & Distributed Transactions
import unittest
import shutil
from pathlib import Path
from pyreact.compiler.lexer import Lexer
from pyreact.compiler.parser import Parser
from pyreact.compiler.codegen import CodeGenerator


class TestFase28(unittest.TestCase):
    def setUp(self):
        self.out_dir = Path("test_db_out")
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)
        self.out_dir.mkdir(exist_ok=True)

    def tearDown(self):
        if self.out_dir.exists():
            shutil.rmtree(self.out_dir, ignore_errors=True)

    # ── helper ────────────────────────────────────────────────────────────────
    def _compile(self, src: str):
        tokens = Lexer(src).tokenize()
        ast = Parser(tokens).parse()
        cg = CodeGenerator(ast, out_dir=self.out_dir)
        cg.generate()
        return ast

    # ── Parser tests ─────────────────────────────────────────────────────────
    def test_database_block_parses_postgresql(self):
        """Database block should parse postgresql configurations."""
        src = """
        database {
            provider = "postgresql"
            url = "postgresql://user:pass@localhost/db"
        }
        component App() {
            return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
        }
        """
        tokens = Lexer(src).tokenize()
        tree = Parser(tokens).parse()
        self.assertIsNotNone(tree.database)
        self.assertEqual(tree.database.provider, "postgresql")
        self.assertEqual(tree.database.url, "postgresql://user:pass@localhost/db")

    # ── CodeGen tests ────────────────────────────────────────────────────────
    def test_postgresql_pooling_generated(self):
        """App.py must configure SQLAlchemy engine connection pooling for postgresql."""
        src = """
        database {
            provider = "postgresql"
            url = "postgresql://user:pass@localhost/db"
        }
        component App() {
            return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        app_path = self.out_dir / "backend" / "app.py"
        self.assertTrue(app_path.exists())
        app_code = app_path.read_text(encoding="utf-8")
        self.assertIn("SQLALCHEMY_ENGINE_OPTIONS", app_code)
        self.assertIn("'pool_size': 10", app_code)
        
        # Check requirements.txt has psycopg2-binary
        reqs_path = self.out_dir / "backend" / "requirements.txt"
        self.assertTrue(reqs_path.exists())
        reqs_txt = reqs_path.read_text(encoding="utf-8")
        self.assertIn("psycopg2-binary", reqs_txt)

    def test_mongodb_provider_requirements(self):
        """Mongodb provider setup must output pymongo client and update requirements."""
        src = """
        database {
            provider = "mongodb"
            url = "mongodb://localhost:27017/db"
        }
        component App() {
            return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        app_path = self.out_dir / "backend" / "app.py"
        self.assertTrue(app_path.exists())
        app_code = app_path.read_text(encoding="utf-8")
        self.assertIn("MongoClient", app_code)
        self.assertIn("maxPoolSize=50", app_code)
        self.assertNotIn("auto_migrate", app_code)
        
        # Check requirements.txt has pymongo
        reqs_path = self.out_dir / "backend" / "requirements.txt"
        reqs_txt = reqs_path.read_text(encoding="utf-8")
        self.assertIn("pymongo", reqs_txt)

    def test_redis_provider_requirements(self):
        """Redis provider setup must initialize redis pool and add redis to requirements."""
        src = """
        database {
            provider = "redis"
            url = "redis://localhost:6379/0"
        }
        component App() {
            return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        app_path = self.out_dir / "backend" / "app.py"
        app_code = app_path.read_text(encoding="utf-8")
        self.assertIn("redis.ConnectionPool.from_url", app_code)
        self.assertIn("redis.Redis", app_code)
        
        # Check requirements.txt has redis
        reqs_path = self.out_dir / "backend" / "requirements.txt"
        reqs_txt = reqs_path.read_text(encoding="utf-8")
        self.assertIn("redis", reqs_txt)

    def test_distributed_transaction_helper_generated(self):
        """transactions.py must contain distributed transaction coordinator and lock managers."""
        src = """
        database {
            provider = "postgresql"
            url = "postgresql://user:pass@localhost/db"
        }
        component App() {
            return (<UI.Page><UI.Text>App</UI.Text></UI.Page>)
        }
        """
        self._compile(src)
        tx_path = self.out_dir / "backend" / "transactions.py"
        self.assertTrue(tx_path.exists(), "transactions.py was not generated")
        content = tx_path.read_text(encoding="utf-8")
        self.assertIn("DistributedTransactionManager", content)
        self.assertIn("RedisLockManager", content)


if __name__ == "__main__":
    unittest.main()
