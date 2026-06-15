"""PYREACT compiler errors mapping and hints helper."""

import re
from typing import Optional

# Mapping of common JavaScript/React patterns to PyReact equivalents and hints
COMMON_MISTAKES = [
    {
        "pattern": r"\buseState\b",
        "hint": "Di PyReact, gunakan `use_state()` bukan `useState()`.",
        "example": "Contoh: val, setVal = use_state(initial_value)",
        "ref": "AGENTS.md#hooks-reference"
    },
    {
        "pattern": r"\buseEffect\b",
        "hint": "Di PyReact, gunakan `use_effect()` bukan `useEffect()`.",
        "example": "Contoh: use_effect(def(): ... , [deps])",
        "ref": "AGENTS.md#hooks-reference"
    },
    {
        "pattern": r"\bconst\b|\blet\b",
        "hint": "Di PyReact, gunakan variabel Python biasa (tanpa `const` atau `let`).",
        "example": "Contoh: name = 'Alice' bukan const name = 'Alice'",
        "ref": "AGENTS.md#things-to-avoid"
    },
    {
        "pattern": r"\bfunction\b",
        "hint": "Di PyReact, gunakan `def` untuk mendeklarasikan fungsi.",
        "example": "Contoh: def my_handler(): bukan function my_handler()",
        "ref": "AGENTS.md#things-to-avoid"
    },
    {
        "pattern": r"===",
        "hint": "Di PyReact, gunakan `==` untuk perbandingan sama dengan.",
        "example": "Contoh: x == y bukan x === y",
        "ref": "AGENTS.md#things-to-avoid"
    },
    {
        "pattern": r"!==",
        "hint": "Di PyReact, gunakan `!=` untuk perbandingan tidak sama dengan.",
        "example": "Contoh: x != y bukan x !== y",
        "ref": "AGENTS.md#things-to-avoid"
    },
    {
        "pattern": r"\bnull\b",
        "hint": "Di PyReact, gunakan `None` untuk merepresentasikan nilai kosong.",
        "example": "Contoh: value = None bukan value = null",
        "ref": "AGENTS.md#things-to-avoid"
    },
    {
        "pattern": r"\btrue\b|\bfalse\b",
        "hint": "Di PyReact, gunakan boolean Python `True` atau `False` (diawali huruf kapital).",
        "example": "Contoh: is_loading = True bukan is_loading = true",
        "ref": "AGENTS.md#things-to-avoid"
    },
    {
        "pattern": r"\bimport\s+React\b|from\s+['\"]react['\"]",
        "hint": "Di PyReact, jangan mengimpor React secara manual. Compiler akan meng-generate otomatis.",
        "example": "Hapus baris import React atau from 'react'",
        "ref": "AGENTS.md#critical-rules"
    },
    {
        "pattern": r"\bfetch\b|\baxios\b",
        "hint": "Di PyReact, gunakan `server.func_name()` untuk memanggil API backend (PyBridge RPC) secara langsung.",
        "example": "Contoh: data = server.get_users() bukan fetch('/api/users')",
        "ref": "AGENTS.md#critical-rules"
    },
    {
        "pattern": r"\bclass\s*=\s*['\"{]",
        "hint": "Di PyReact JSX, gunakan `className=` bukan `class=` untuk kelas CSS (Tailwind).",
        "example": "Contoh: <div className=\"flex\"> bukan <div class=\"flex\">",
        "ref": "AGENTS.md#2-component-name-ui-components"
    },
    {
        "pattern": r"\bexport\s+(?:default\s+)?\b",
        "hint": "Di PyReact, komponen tidak perlu di-export secara manual. Cukup gunakan deklarasi `component NamaKomponen():`.",
        "example": "Contoh: component Home(): bukan export default function Home()",
        "ref": "AGENTS.md#2-component-name-ui-components"
    },
    {
        "pattern": r"\b(Server|Component|Style|Database|Dependencies|Shared_state|Realtime|Graphql|Rbac|Webrtc|Middleware|Locale|Pages)\s*[\{:]",
        "hint": "Di PyReact, keyword blok harus diawali dengan huruf kecil (lowercase).",
        "example": "Contoh: server { } bukan Server { }",
        "ref": "AGENTS.md#file-structure"
    },
    {
        "pattern": r"^\s*//",
        "hint": "Di PyReact (sisi Python), gunakan `#` bukan `//` untuk komentar.",
        "example": "Contoh: # Ini komentar bukan // Ini komentar",
        "ref": "AGENTS.md#syntax-convention"
    }
]

def get_line_hint(line_content: str) -> Optional[dict]:
    """Analyze a single line of code for common mistakes and return the first matching hint."""
    for mistake in COMMON_MISTAKES:
        if re.search(mistake["pattern"], line_content):
            return mistake
    return None

def analyze_source_for_hints(source: str) -> list[str]:
    """Scan the entire source code for common mistakes and return a list of hints with line numbers."""
    hints = []
    lines = source.splitlines()
    for idx, line in enumerate(lines, 1):
        # Skip comment lines
        if line.strip().startswith("#"):
            continue
        match = get_line_hint(line)
        if match:
            hints.append(
                f"Baris {idx}: {match['hint']}\n"
                f"  {match['example']}\n"
                f"  Lihat: {match['ref']}"
            )
    return hints

def validate_source_integrity(source: str):
    """Scan the source for critical mistakes and raise ParseError if found."""
    from pyreact.compiler.parser import ParseError
    lines = source.splitlines()
    for idx, line in enumerate(lines, 1):
        # Ignore comments and string literals that might contain references
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        # Check each mistake
        match = get_line_hint(line)
        if match:
            m = re.search(match["pattern"], line)
            word = m.group(0) if m else "syntax"
            col = (m.start() + 1) if m else (line.find(word) + 1)
            raise ParseError(
                message=f"Sintaksis tidak valid: Menggunakan '{word.strip()}' yang tidak didukung.",
                line=idx,
                col=max(1, col),
                suggestion=f"{match['hint']} {match['example']} (Rujukan: {match['ref']})"
            )

def format_compilation_error(error_msg: str, line: int, col: int, source: str, suggestion: str = "") -> str:
    """Format a compiler error with detailed code frame, error message, and suggestions/hints."""
    lines = source.splitlines()
    result = []
    
    # 1. Title/Header
    result.append(f"\n  X  Compilation Error at line {line}, col {col}:\n")
    
    # 2. Code frame (with 2 lines of context before and after)
    if 1 <= line <= len(lines):
        start_line = max(1, line - 2)
        end_line = min(len(lines), line + 2)
        for ln in range(start_line, end_line + 1):
            prefix = ">>" if ln == line else "  "
            result.append(f"  {prefix} {ln} | {lines[ln - 1]}")
            if ln == line and col > 0:
                prefix_len = 8 + len(str(line))
                indent = " " * (prefix_len + col - 1)
                result.append(f"{indent}^")
            
    # 3. Error message
    result.append(f"\n  Error: {error_msg}")
    
    # 4. Contextual Hint (Specific to the error line)
    err_line_content = lines[line - 1] if 1 <= line <= len(lines) else ""
    line_hint = get_line_hint(err_line_content)
    
    if line_hint:
        result.append(f"\n  Hint: {line_hint['hint']}")
        result.append(f"  {line_hint['example']}")
        result.append(f"  Lihat: {line_hint['ref']}")
    elif suggestion:
        result.append(f"\n  Hint: {suggestion}")
        
    # 5. Global lint-style suggestions for other mistakes in the file
    other_hints = []
    for idx, l in enumerate(lines, 1):
        if idx == line:
            continue  # Already handled above
        if l.strip().startswith("#"):
            continue
        m = get_line_hint(l)
        if m:
            other_hints.append(f"Line {idx}: Gunakan `{m['pattern'].replace(r'\\b', '')}`? -> {m['hint']}")
            
    if other_hints:
        result.append("\n  Saran perbaikan lainnya dalam file ini:")
        for oh in other_hints[:3]:  # Show at most 3 other hints
            result.append(f"    - {oh}")
            
    result.append("\n  TIP: Jalankan dengan --heal untuk perbaikan otomatis via AI\n")
    return "\n".join(result)
