import os
import json
import shutil
from pathlib import Path
import pytest
from pyreact.cli import cmd_env, cmd_db, cmd_deploy

@pytest.fixture(autouse=True)
def setup_teardown_project():
    # Setup temporary test environment
    # Backup files if they exist
    backups = {}
    files_to_clean = [
        ".env.pyreact",
        "vercel.json",
        "Dockerfile",
        "railway.json",
        "fly.toml",
        "render.yaml",
        "app.yaml",
        "app.pyreact",
        ".pyreact_db_state.json",
        "tasks.db"
    ]
    for f in files_to_clean:
        p = Path(f)
        if p.exists():
            backups[f] = p.read_text(encoding="utf-8", errors="replace")
            p.unlink()

    migrations_backup = None
    if Path("migrations").exists():
        migrations_backup = list(Path("migrations").glob("*"))
        shutil.rmtree("migrations")
        
    yield
    
    # Teardown: clean generated files
    for f in files_to_clean:
        p = Path(f)
        if p.exists():
            p.unlink()
            
    if Path("migrations").exists():
        shutil.rmtree("migrations")
        
    # Restore backups
    for f, content in backups.items():
        Path(f).write_text(content, encoding="utf-8")
        
    if migrations_backup:
        Path("migrations").mkdir(exist_ok=True)
        for f in migrations_backup:
            shutil.copy(f, "migrations")

def test_env_check(capsys):
    # Test 1: No file
    cmd_env(["check"])
    captured = capsys.readouterr()
    assert "Warning: .env.pyreact file not found" in captured.out

    # Test 2: Valid and invalid keys
    env_content = (
        "SERVER_DB_URL=sqlite:///test.db\n"
        "PUBLIC_API_KEY=12345\n"
        "invalid_key=abc\n"
        "SERVER_lowercase=def\n"
    )
    Path(".env.pyreact").write_text(env_content, encoding="utf-8")
    
    # Mock app.pyreact that uses SERVER_DB_URL and SERVER_MISSING
    app_content = (
        "server {\n"
        "    db_url = os.environ.get('SERVER_DB_URL')\n"
        "    missing = os.environ.get('SERVER_MISSING')\n"
        "}\n"
    )
    Path("app.pyreact").write_text(app_content, encoding="utf-8")
    
    cmd_env(["check"])
    captured = capsys.readouterr()
    assert "Must start with SERVER_ or PUBLIC_" in captured.out
    assert "Must be all UPPERCASE" in captured.out
    assert "SERVER_MISSING" in captured.out

def test_db_migrations(capsys):
    # Create app.pyreact with DB configuration
    app_content = (
        "database {\n"
        "    provider = \"sqlite\"\n"
        "    url = \"test_migrate.db\"\n"
        "}\n"
        "server {\n"
        "    class DbProduct(db.Model):\n"
        "        id = db.Column(db.Integer, primary_key=True)\n"
        "        name = db.Column(db.String(100), nullable=False)\n"
        "        price = db.Column(db.Integer)\n"
        "}\n"
    )
    Path("app.pyreact").write_text(app_content, encoding="utf-8")
    
    # 1. Run migrate
    cmd_db(["migrate"])
    captured = capsys.readouterr()
    assert "Running migration for provider 'sqlite'" in captured.out
    assert "Generated migration file" in captured.out
    assert "Generated rollback file" in captured.out
    
    migrations = list(Path("migrations").glob("*.sql"))
    assert len(migrations) == 2  # One migrate, one rollback
    
    state_file = Path(".pyreact_db_state.json")
    assert state_file.exists()
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert len(state["migrations"]) == 1
    assert state["migrations"][0]["status"] == "applied"
    
    # 2. Run status
    cmd_db(["status"])
    captured = capsys.readouterr()
    assert "applied" in captured.out
    assert "migration_" in captured.out
    
    # 3. Run rollback
    cmd_db(["rollback"])
    captured = capsys.readouterr()
    assert "Rolling back migration" in captured.out
    assert "rolled back successfully" in captured.out
    
    state = json.loads(state_file.read_text(encoding="utf-8"))
    assert state["migrations"][0]["status"] == "rolled_back"

def test_deploy_platforms(capsys):
    # Test Vercel
    cmd_deploy(["--platform", "vercel"])
    assert Path("vercel.json").exists()
    assert "dist/frontend/**/*" in json.loads(Path("vercel.json").read_text(encoding="utf-8"))["builds"][0]["src"]
    
    # Test Fly
    cmd_deploy(["--platform", "fly"])
    assert Path("Dockerfile").exists()
    assert Path("fly.toml").exists()
    assert "internal_port = 8080" in Path("fly.toml").read_text(encoding="utf-8")

    # Test Railway
    cmd_deploy(["--platform", "railway"])
    assert Path("railway.json").exists()

    # Test Render
    cmd_deploy(["--platform", "render"])
    assert Path("render.yaml").exists()

    # Test DigitalOcean
    cmd_deploy(["--platform", "digitalocean"])
    assert Path("app.yaml").exists()
