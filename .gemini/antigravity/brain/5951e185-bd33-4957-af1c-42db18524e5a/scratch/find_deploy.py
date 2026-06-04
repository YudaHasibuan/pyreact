from pathlib import Path

content = Path("pyreact/cli.py").read_text(encoding="utf-8")
for idx, line in enumerate(content.splitlines()):
    if "deploy" in line:
        print(f"Line {idx + 1}: {line}")
