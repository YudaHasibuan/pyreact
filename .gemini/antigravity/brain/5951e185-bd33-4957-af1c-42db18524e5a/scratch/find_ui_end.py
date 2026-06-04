from pathlib import Path

content = Path("pyreact/compiler/codegen.py").read_text(encoding="utf-8")
lines = content.splitlines()

# Search for the end of UI_COMPONENTS_JSX (which is followed by another constant or double quotes)
in_block = False
start_line = 0
for idx, line in enumerate(lines):
    if "UI_COMPONENTS_JSX =" in line:
        in_block = True
        start_line = idx + 1
    elif in_block and line == '"""':
        print(f"UI_COMPONENTS_JSX starts at {start_line}, ends at line {idx + 1}")
        break
