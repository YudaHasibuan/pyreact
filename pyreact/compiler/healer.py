"""PYREACT Self-Healing Compiler Engine — Fase 15
Memanggil model Ollama lokal (localhost:11434) untuk menganalisis dan
memperbaiki syntax error / parsing error secara otomatis.

Fitur:
  - Multi-model support (llama3, codellama, qwen2.5-coder, dsb)
  - Iterative retry healing (hingga MAX_RETRIES kali)
  - Backup otomatis sebelum menulis ulang file
  - Diff viewer: tampilkan perubahan sebelum & sesudah
  - Streaming token output (opsional)
  - Fallback rule-based healer saat Ollama offline
"""
from __future__ import annotations

import json
import re
import sys
import shutil
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, List


# ── Konfigurasi ───────────────────────────────────────────────────────────────

OLLAMA_BASE_URL  = "http://localhost:11434"
OLLAMA_API       = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_API  = f"{OLLAMA_BASE_URL}/api/tags"

# Urutan preferensi model — healer akan mencoba yang tersedia pertama
PREFERRED_MODELS = [
    "codellama",
    "qwen2.5-coder",
    "deepseek-coder",
    "llama3",
    "llama3.2",
    "mistral",
    "phi3",
    "gemma2",
]

MAX_RETRIES   = 3     # jumlah maksimum iterasi healing
TIMEOUT_SEC   = 60    # timeout Ollama per request (detik)
TEMPERATURE   = 0.1   # rendah agar output deterministik


# ── ANSI colour helpers ───────────────────────────────────────────────────────

def _c(text: str, code: str) -> str:
    """Wrap text with ANSI colour code (only on non-Windows or utf-8 terminal)."""
    try:
        # Only apply ANSI if stdout supports it
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return f"\033[{code}m{text}\033[0m"
        return text
    except Exception:
        return text

def _safe_print(msg: str) -> None:
    """Print dengan fallback untuk Windows console yang tidak mendukung Unicode."""
    try:
        print(msg)
    except UnicodeEncodeError:
        # Encode ke ASCII, ganti char yang tidak bisa dikodekan dengan '?'
        safe = msg.encode('ascii', errors='replace').decode('ascii')
        print(safe)

def _green(t):  return _c(t, "32")
def _red(t):    return _c(t, "31")
def _yellow(t): return _c(t, "33")
def _cyan(t):   return _c(t, "36")
def _bold(t):   return _c(t, "1")
def _dim(t):    return _c(t, "2")


# ── Ollama helpers ────────────────────────────────────────────────────────────

def _get_available_models() -> List[str]:
    """Kembalikan daftar nama model LENGKAP (dengan tag) yang tersedia di Ollama lokal."""
    try:
        with urllib.request.urlopen(OLLAMA_TAGS_API, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # Kembalikan nama LENGKAP model agar API request tidak 404
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def _pick_model() -> Optional[str]:
    """Pilih model terbaik yang tersedia berdasarkan urutan preferensi."""
    available = _get_available_models()
    if not available:
        return None
    # Coba cocokkan preferred model dengan nama yang tersedia
    for preferred in PREFERRED_MODELS:
        for avail in available:
            # avail bisa berupa 'gemma4:latest', 'llama3:8b', dsb.
            base_name = avail.split(":")[0].lower()
            if preferred.lower() in base_name:
                return avail  # kembalikan nama LENGKAP
    # Fallback: gunakan model pertama yang tersedia
    return available[0] if available else None


def _call_ollama(model: str, prompt: str, system: str = "") -> str:
    """Panggil Ollama API dan kembalikan response string (non-streaming)."""
    payload = {
        "model":   model,
        "prompt":  prompt,
        "system":  system,
        "stream":  False,
        "options": {
            "temperature":   TEMPERATURE,
            "num_predict":   4096,
            "stop":          ["```"],
        },
    }
    req = urllib.request.Request(
        OLLAMA_API,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("response", "").strip()


def _strip_markdown_fence(code: str) -> str:
    """Hapus code fence markdown (``` atau ```pyreact) dari awal/akhir."""
    code = code.strip()
    # Coba strip dengan regex multi-line
    import re as _re
    # Hapus opening fence: ```pyreact atau ```
    code = _re.sub(r'^```[a-zA-Z]*\s*\n?', '', code)
    # Hapus closing fence
    code = _re.sub(r'\n?```\s*$', '', code)
    return code.strip()


# ── Backup helpers ────────────────────────────────────────────────────────────

def _make_backup(entry_path: Path) -> Path:
    """Buat backup file sebelum menulis ulang, kembalikan path backup."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = entry_path.parent / ".pyreact_heal_backups"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / f"{entry_path.stem}.{ts}.bak.pyreact"
    shutil.copy2(str(entry_path), str(backup_path))
    return backup_path


# ── Diff viewer ───────────────────────────────────────────────────────────────

def _show_diff(original: str, healed: str, max_lines: int = 40) -> None:
    """Tampilkan diff sederhana antara kode asli dan kode yang diperbaiki."""
    orig_lines   = original.splitlines()
    healed_lines = healed.splitlines()
    print(_bold("\n  [HEAL] Perubahan yang dilakukan oleh AI:\n"))

    shown = 0
    i = j = 0
    while i < len(orig_lines) and j < len(healed_lines):
        if orig_lines[i] == healed_lines[j]:
            i += 1; j += 1
        else:
            # Tampilkan konteks
            if orig_lines[i].strip():
                print(_red(f"  - {orig_lines[i]}"))
                shown += 1
            if healed_lines[j].strip():
                print(_green(f"  + {healed_lines[j]}"))
                shown += 1
            i += 1; j += 1
        if shown >= max_lines:
            print(_dim("  ... (diff dipotong, terlalu banyak perubahan)"))
            break

    # Sisa baris baru
    while j < len(healed_lines) and healed_lines[j].strip():
        print(_green(f"  + {healed_lines[j]}"))
        j += 1; shown += 1
        if shown >= max_lines:
            break

    print()


# ── Rule-based fallback healer ────────────────────────────────────────────────

class RuleBasedHealer:
    """
    Healer sederhana berbasis aturan sebagai fallback saat Ollama offline.
    Memperbaiki kesalahan sintaks umum pada kode PyReact.
    """

    RULES = [
        # (pattern, replacement, description)
        (r'component\s+(\w+)\s*\(\s*\)\s*\{',
         r'component \1():', "Ubah brace-syntax component menjadi colon-syntax"),
        (r'server\s*:\s*\{', r'server {', "Hapus colon sebelum brace server"),
        (r'use_state\(([^)]*)\)\s*\n',
         r'use_state(\1)\n', "Perbaiki use_state"),
        # Tambahkan aturan sesuai kebutuhan
    ]

    def heal(self, source: str, error_msg: str) -> Optional[str]:
        """Terapkan aturan berbasis regex, kembalikan None jika tidak ada yang cocok."""
        result = source
        applied_any = False
        for pattern, replacement, desc in self.RULES:
            new_result = re.sub(pattern, replacement, result)
            if new_result != result:
                result = new_result
                applied_any = True
                print(_yellow(f"    [Rule] Applied: {desc}"))
        return result if applied_any else None


# ── Healing prompt builder ────────────────────────────────────────────────────

def _build_heal_prompt(source: str, error_msg: str,
                        err_line: int = 0, err_col: int = 0,
                        attempt: int = 1) -> Tuple[str, str]:
    """
    Bangun system prompt dan user prompt untuk self-healing.
    Kembalikan (system_prompt, user_prompt).
    """
    system_prompt = (
        "You are an expert compiler and code fixer for the PyReact programming language. "
        "PyReact uses a custom DSL with blocks: server { }, component Name(): ..., style { }, "
        "model Name: { }, database { }, dependencies { }, shared_state { }, agent Name { }, "
        "pipeline Name { }, pages { }. "
        "When given source code with a compile error, you must return ONLY the corrected "
        "source code with the error fixed. "
        "Do NOT include markdown code fences, explanations, or comments outside the code. "
        "Return only the raw corrected PyReact source code."
    )

    location_hint = ""
    if err_line > 0:
        lines = source.splitlines()
        start = max(0, err_line - 3)
        end   = min(len(lines), err_line + 2)
        context_lines = "\n".join(
            f"  {'>>>' if i + 1 == err_line else '   '} {i+1}: {lines[i]}"
            for i in range(start, end)
        )
        location_hint = f"\n\n[Error Location (Line {err_line}, Col {err_col})]\n{context_lines}"

    retry_hint = ""
    if attempt > 1:
        retry_hint = (
            f"\n\nNOTE: This is attempt #{attempt}. The previous fix was not sufficient. "
            "Please carefully re-analyze the full source code and apply a more thorough fix."
        )

    user_prompt = f"""Fix the following PyReact source code that has a compilation error.

[Compiler Error]
{error_msg}{location_hint}{retry_hint}

[PyReact Source Code to Fix]
{source}

Return ONLY the corrected PyReact source code. No explanations. No markdown.
"""
    return system_prompt, user_prompt


# ── Compilation attempt helper ────────────────────────────────────────────────

def _try_compile(source: str) -> Optional[Exception]:
    """
    Coba lex + parse source code.
    Kembalikan None jika sukses, atau Exception jika gagal.
    """
    import sys as _sys
    # Ensure pyreact is importable
    proj_root = str(Path(__file__).parent.parent.parent)
    if proj_root not in _sys.path:
        _sys.path.insert(0, proj_root)

    from pyreact.compiler.lexer import Lexer, LexerError
    from pyreact.compiler.parser import Parser, ParseError
    try:
        tokens = Lexer(source).tokenize()
        Parser(tokens).parse()
        return None
    except (LexerError, ParseError, Exception) as e:
        return e


# ── Main public API ───────────────────────────────────────────────────────────

class SelfHealingCompiler:
    """
    Mesin Self-Healing Compiler untuk PyReact.

    Penggunaan:
        healer = SelfHealingCompiler(entry_path="app.pyreact", source=src, error=err)
        success, healed_source = healer.heal()
    """

    def __init__(
        self,
        entry_path: str,
        source: str,
        error: Exception,
        model: Optional[str] = None,
        show_diff: bool = True,
        make_backup: bool = True,
        max_retries: int = MAX_RETRIES,
        verbose: bool = True,
    ):
        self.entry_path  = Path(entry_path)
        self.source      = source
        self.error       = error
        self.model       = model
        self.show_diff   = show_diff
        self.make_backup = make_backup
        self.max_retries = max_retries
        self.verbose     = verbose

        self.err_msg  = str(error)
        self.err_line = getattr(error, "line", 0)
        self.err_col  = getattr(error, "col", 0)

    def _log(self, msg: str) -> None:
        if self.verbose:
            _safe_print(msg)

    def _select_model(self) -> Optional[str]:
        """Pilih model: gunakan yang dispesifikasikan user, atau auto-detect."""
        if self.model:
            return self.model
        self._log(_cyan("  [HEAL] Mendeteksi model Ollama yang tersedia..."))
        model = _pick_model()
        if model:
            self._log(_cyan(f"  [HEAL] Model terpilih: {_bold(model)}"))
        else:
            self._log(_yellow("  [HEAL] Tidak ada model Ollama yang ditemukan."))
        return model

    def heal(self) -> Tuple[bool, Optional[str]]:
        """
        Jalankan proses self-healing.
        Kembalikan (success: bool, healed_source: Optional[str]).
        """
        _safe_print(_bold("\n  +==================================================+"))
        _safe_print(_bold("  |    PyReact Self-Healing Compiler  [Fase 15]     |" ))
        _safe_print(_bold("  +==================================================+"))
        self._log(_red(f"\n  [ERROR] Kompilasi gagal: {self.err_msg}"))
        if self.err_line:
            self._log(_red(f"  [ERROR] Lokasi: Baris {self.err_line}, Kolom {self.err_col}"))

        # ── Coba dengan AI (Ollama) ─────────────────────────────────────────
        model = self._select_model()

        if model:
            result = self._ai_heal(model)
            if result is not None:
                return True, result

        # ── Fallback ke rule-based healer ───────────────────────────────────
        self._log(_yellow("\n  [HEAL] Mencoba Rule-Based Healer sebagai fallback..."))
        rule_healer = RuleBasedHealer()
        rule_fixed  = rule_healer.heal(self.source, self.err_msg)

        if rule_fixed:
            err = _try_compile(rule_fixed)
            if err is None:
                self._log(_green("  [HEAL] Rule-Based Healer berhasil!"))
                self._apply_fix(rule_fixed)
                return True, rule_fixed
            else:
                self._log(_red(f"  [HEAL] Rule-based fix masih gagal: {err}"))

        self._log(_red("\n  [HEAL] Self-Healing gagal setelah semua upaya."))
        self._log(_yellow("  [TIP]  Periksa error di atas dan perbaiki kode secara manual."))
        return False, None

    def _ai_heal(self, model: str) -> Optional[str]:
        """Iterative AI healing dengan retry hingga MAX_RETRIES."""
        current_source = self.source
        current_error  = self.err_msg

        for attempt in range(1, self.max_retries + 1):
            self._log(_cyan(
                f"\n  [HEAL] Mengirim ke {_bold(model)} via Ollama "
                f"(Percobaan {attempt}/{self.max_retries})..."
            ))
            self._log(_dim("  [HEAL] Menunggu respons AI..."))

            try:
                sys_prompt, usr_prompt = _build_heal_prompt(
                    current_source, current_error,
                    self.err_line, self.err_col, attempt
                )
                raw_response = _call_ollama(model, usr_prompt, sys_prompt)
                healed_code  = _strip_markdown_fence(raw_response)

                if not healed_code:
                    self._log(_yellow("  [HEAL] AI mengembalikan respons kosong."))
                    continue

                self._log(_green(f"  [HEAL] AI mengembalikan {len(healed_code)} karakter kode."))

                # Validasi: apakah kode yang diperbaiki bisa dikompilasi?
                compile_err = _try_compile(healed_code)
                if compile_err is None:
                    self._log(_bold(_green(
                        f"\n  [HEAL] Self-Healing BERHASIL pada percobaan ke-{attempt}!"
                    )))
                    if self.show_diff:
                        _show_diff(self.source, healed_code)
                    self._apply_fix(healed_code)
                    return healed_code
                else:
                    self._log(_yellow(
                        f"  [HEAL] Kode yang diperbaiki masih punya error: {compile_err}"
                    ))
                    # Update untuk iterasi berikutnya
                    current_source = healed_code
                    current_error  = str(compile_err)

            except urllib.error.URLError as e:
                self._log(_red(f"  [HEAL] Koneksi ke Ollama gagal: {e}"))
                self._log(_yellow(
                    "  [TIP]  Pastikan Ollama berjalan: `ollama serve` "
                    "dan model tersedia: `ollama pull llama3`"
                ))
                return None
            except Exception as e:
                self._log(_red(f"  [HEAL] Error saat healing percobaan {attempt}: {e}"))

        self._log(_red(f"  [HEAL] Gagal setelah {self.max_retries} percobaan AI."))
        return None

    def _apply_fix(self, healed_code: str) -> None:
        """Simpan backup dan tulis kode yang sudah diperbaiki ke file."""
        if self.make_backup:
            backup_path = _make_backup(self.entry_path)
            self._log(_dim(f"  [HEAL] Backup disimpan: {backup_path}"))

        self.entry_path.write_text(healed_code, encoding="utf-8")
        self._log(_green(f"  [HEAL] File '{self.entry_path}' telah diperbarui."))


# ── Convenience function untuk CLI ───────────────────────────────────────────

def auto_heal(
    entry: str,
    source: str,
    error: Exception,
    model: Optional[str] = None,
    show_diff: bool = True,
    make_backup: bool = True,
    max_retries: int = MAX_RETRIES,
) -> Tuple[bool, Optional[str]]:
    """
    Fungsi convenience untuk memanggil SelfHealingCompiler dari CLI.

    Returns:
        (success, healed_source) — healed_source adalah kode yang sudah diperbaiki,
        atau None jika gagal.
    """
    healer = SelfHealingCompiler(
        entry_path=entry,
        source=source,
        error=error,
        model=model,
        show_diff=show_diff,
        make_backup=make_backup,
        max_retries=max_retries,
    )
    return healer.heal()


# ── CLI standalone mode ───────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Mode standalone: python -m pyreact.compiler.healer <file.pyreact>
    Berguna untuk debugging dan testing healer secara langsung.
    """
    import sys as _sys
    if len(_sys.argv) < 2:
        print("Usage: python -m pyreact.compiler.healer <file.pyreact>")
        _sys.exit(1)

    path   = Path(_sys.argv[1])
    source = path.read_text(encoding="utf-8")

    # Coba compile terlebih dahulu
    err = _try_compile(source)
    if err is None:
        print(_green(f"[OK] '{path}' sudah valid, tidak perlu healing."))
        _sys.exit(0)

    success, _ = auto_heal(str(path), source, err)
    _sys.exit(0 if success else 1)
