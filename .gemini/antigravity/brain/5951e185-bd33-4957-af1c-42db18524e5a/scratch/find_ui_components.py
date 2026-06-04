from pathlib import Path

content = Path("pyreact/compiler/codegen.py").read_text(encoding="utf-8")
for idx, line in enumerate(content.splitlines()):
    if "UI_COMPONENTS_JSX" in line and "=" in line:
        print(f"Line {idx + 1}: {line}")
