"""PYREACT Lexer v0.1 — tokenizes .pyreact source files.
Supports both brace syntax (server { }) and Python-indent syntax (component X():).
"""
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class TT(Enum):
    SERVER = auto(); COMPONENT = auto(); STYLE = auto(); MODEL = auto()
    DATABASE = auto(); DEPENDENCIES = auto(); SHARED_STATE = auto()
    AGENT = auto(); PIPELINE = auto(); PAGES = auto(); REALTIME = auto()
    GRAPHQL = auto(); RBAC = auto(); WEBRTC = auto()
    LBRACE = auto(); RBRACE = auto(); LPAREN = auto(); RPAREN = auto()
    COLON = auto(); COMMA = auto(); EQUALS = auto(); NEWLINE = auto()
    IDENTIFIER = auto(); STRING = auto(); NUMBER = auto(); BOOL = auto()
    RAW_PYTHON = auto(); COMMENT = auto(); EOF = auto()


@dataclass
class Token:
    type: TT
    value: str
    line: int
    col: int
    def __repr__(self): return f"Token({self.type.name}, {self.value!r}, L{self.line})"


KEYWORDS = {
    "server": TT.SERVER, "component": TT.COMPONENT,
    "style": TT.STYLE, "model": TT.MODEL,
    "database": TT.DATABASE, "dependencies": TT.DEPENDENCIES,
    "shared_state": TT.SHARED_STATE,
    "agent": TT.AGENT, "pipeline": TT.PIPELINE,
    "pages": TT.PAGES, "realtime": TT.REALTIME,
    "graphql": TT.GRAPHQL, "rbac": TT.RBAC, "webrtc": TT.WEBRTC,
    "True": TT.BOOL, "False": TT.BOOL,
}
TokenType = TT  # alias for compat


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        src = self.source
        while self.pos < len(src):
            self._skip_ws()
            if self.pos >= len(src):
                break
            ch = src[self.pos]

            if ch == '\n':
                self.tokens.append(Token(TT.NEWLINE, '\n', self.line, self.col))
                self.line += 1; self.col = 1; self.pos += 1
                continue

            if ch == '#':
                end = src.find('\n', self.pos)
                if end == -1: end = len(src)
                self.tokens.append(Token(TT.COMMENT, src[self.pos:end], self.line, self.col))
                self.col += end - self.pos; self.pos = end
                continue

            if ch in ('"', "'"):
                self.tokens.append(self._read_string())
                continue

            if ch.isdigit():
                self.tokens.append(self._read_number())
                continue

            SC = {'{': TT.LBRACE, '}': TT.RBRACE, '(': TT.LPAREN,
                  ')': TT.RPAREN, ':': TT.COLON, ',': TT.COMMA, '=': TT.EQUALS}
            if ch in SC:
                self.tokens.append(Token(SC[ch], ch, self.line, self.col))
                self.pos += 1; self.col += 1
                continue

            if ch.isalpha() or ch == '_':
                tok = self._read_ident()
                self.tokens.append(tok)
                if tok.type in (TT.SERVER, TT.STYLE, TT.COMPONENT, TT.MODEL, TT.DATABASE, TT.DEPENDENCIES, TT.SHARED_STATE, TT.AGENT, TT.PIPELINE, TT.PAGES, TT.REALTIME, TT.GRAPHQL, TT.RBAC, TT.WEBRTC):
                    self._emit_block()
                continue

            self.pos += 1; self.col += 1  # skip unknown

        self.tokens.append(Token(TT.EOF, '', self.line, self.col))
        return self.tokens

    def _emit_block(self):
        """After a block keyword: scan header line then emit LBRACE RAW_PYTHON RBRACE."""
        src = self.source
        # find first '{' or '\n' from current pos (still on header line)
        p = self.pos
        while p < len(src) and src[p] != '{' and src[p] != '\n':
            p += 1

        if p < len(src) and src[p] == '{':
            # ── brace syntax ─────────────────────────────────────────────────
            self._tok_inline(src[self.pos:p])  # tokenise header remainder
            self.pos = p
            self.tokens.append(Token(TT.LBRACE, '{', self.line, self.col))
            self.pos += 1; self.col += 1
            body = self._brace_body()
            self.tokens.append(Token(TT.RAW_PYTHON, body, self.line, self.col))
            if self.pos < len(src) and src[self.pos] == '}':
                self.tokens.append(Token(TT.RBRACE, '}', self.line, self.col))
                self.pos += 1; self.col += 1
        else:
            # ── indent syntax ────────────────────────────────────────────────
            self._tok_inline(src[self.pos:p])
            self.pos = p
            if self.pos < len(src) and src[self.pos] == '\n':
                self.line += 1; self.col = 1; self.pos += 1
            body = self._indent_body()
            self.tokens.append(Token(TT.LBRACE, '{', self.line, self.col))
            self.tokens.append(Token(TT.RAW_PYTHON, body, self.line, self.col))
            self.tokens.append(Token(TT.RBRACE, '}', self.line, self.col))

    def _tok_inline(self, text: str):
        """Tokenise a short header fragment, advance pos/col by len(text)."""
        for m in re.finditer(r'[A-Za-z_]\w*|[(),:=]', text):
            v = m.group()
            SC2 = {'(': TT.LPAREN, ')': TT.RPAREN, ':': TT.COLON, ',': TT.COMMA, '=': TT.EQUALS}
            tt = SC2.get(v) or KEYWORDS.get(v, TT.IDENTIFIER)
            self.tokens.append(Token(tt, v, self.line, self.col + m.start()))
        self.col += len(text)
        self.pos += len(text)

    def _brace_body(self) -> str:
        src = self.source; depth = 1; start = self.pos
        while self.pos < len(src) and depth > 0:
            ch = src[self.pos]
            if ch == '{': depth += 1
            elif ch == '}': depth -= 1
            if depth > 0:
                if ch == '\n': self.line += 1; self.col = 1
                else: self.col += 1
                self.pos += 1
        return src[start:self.pos]

    def _indent_body(self) -> str:
        """Consume lines that start with whitespace. Stop at non-indented non-blank."""
        src = self.source; lines = []
        while self.pos < len(src):
            if src[self.pos] in (' ', '\t'):
                end = src.find('\n', self.pos)
                if end == -1: end = len(src)
                lines.append(src[self.pos:end])
                self.pos = end
                if self.pos < len(src) and src[self.pos] == '\n':
                    self.line += 1; self.col = 1; self.pos += 1
            elif src[self.pos] == '\n':
                lines.append('')
                self.line += 1; self.col = 1; self.pos += 1
            else:
                break
        return '\n'.join(lines)

    def _skip_ws(self):
        src = self.source
        while self.pos < len(src) and src[self.pos] in (' ', '\t', '\r'):
            self.pos += 1; self.col += 1

    def _read_string(self) -> Token:
        src = self.source; sl = self.line; sc = self.col
        q = src[self.pos]
        triple = src[self.pos:self.pos+3] in ('"""', "'''")
        delim = src[self.pos:self.pos+3] if triple else q
        start = self.pos; self.pos += len(delim); self.col += len(delim)
        while self.pos < len(src):
            if src[self.pos:self.pos+len(delim)] == delim:
                self.pos += len(delim); self.col += len(delim); break
            if src[self.pos] == '\n': self.line += 1; self.col = 1
            else: self.col += 1
            self.pos += 1
        return Token(TT.STRING, src[start:self.pos], sl, sc)

    def _read_number(self) -> Token:
        src = self.source; start = self.pos; sc = self.col
        while self.pos < len(src) and (src[self.pos].isdigit() or src[self.pos] == '.'):
            self.pos += 1; self.col += 1
        return Token(TT.NUMBER, src[start:self.pos], self.line, sc)

    def _read_ident(self) -> Token:
        src = self.source; start = self.pos; sc = self.col
        while self.pos < len(src) and (src[self.pos].isalnum() or src[self.pos] == '_'):
            self.pos += 1; self.col += 1
        v = src[start:self.pos]
        return Token(KEYWORDS.get(v, TT.IDENTIFIER), v, self.line, sc)
