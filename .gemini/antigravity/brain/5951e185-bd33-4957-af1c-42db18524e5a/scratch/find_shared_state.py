from pathlib import Path

codegen_path = Path("pyreact/compiler/codegen.py")
content = codegen_path.read_text(encoding="utf-8")
lines = content.splitlines()

for idx, line in enumerate(lines):
    if "shared_state" in line or "SharedState" in line:
        print(f"Line {idx + 1}: {line}")
