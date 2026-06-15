"""PYREACT Parser v0.1 — builds AST from token stream."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from .lexer import Token, TT


# ── AST Nodes ────────────────────────────────────────────────────────────────

@dataclass
class ProgramNode:
    server:       Optional["ServerBlock"]       = None
    components:   List["ComponentNode"]         = field(default_factory=list)
    style:        Optional["StyleBlock"]        = None
    models:       List["ModelNode"]             = field(default_factory=list)
    database:     Optional["DatabaseBlock"]     = None
    dependencies: Optional["DependenciesBlock"] = None
    shared_state: Optional["SharedStateBlock"]  = None
    agents:       List["AgentNode"]             = field(default_factory=list)
    pipelines:    List["PipelineNode"]          = field(default_factory=list)
    pages:        Optional["PagesBlock"]        = None
    realtime:     Optional["RealtimeBlock"]     = None
    graphql:      Optional["GraphQLBlock"]      = None
    rbac:         Optional["RBACBlock"]         = None
    webrtc:       Optional["WebRTCBlock"]       = None
    middleware:   Optional["MiddlewareBlock"]   = None
    locale:       Optional["LocaleBlock"]       = None  # i18n support
    hooks:        List["HookNode"]              = field(default_factory=list)


@dataclass
class LocaleBlock:
    """i18n / Internationalization support."""
    default: str = "en"
    supported: List[str] = field(default_factory=lambda: ["en"])
    translations: Dict[str, Dict[str, str]] = field(default_factory=dict)
    raw: str = ""


@dataclass
class MiddlewareBlock:
    """Fase — Middleware / Request Interceptors."""
    raw: str = ""
    functions: List[FuncDef] = field(default_factory=list)


@dataclass
class WebRTCBlock:
    """Fase 27 – WebRTC P2P & Audio/Video Streaming."""
    signaling: str = "websockets"
    codecs: List[str] = field(default_factory=list)
    raw: str = ""


@dataclass
class RealtimeBlock:
    provider: str = "websockets"
    channels: List[str] = field(default_factory=list)
    raw: str = ""
    functions: List["FuncDef"] = field(default_factory=list)


@dataclass
class GraphQLBlock:
    """Fase 25 – GraphQL API Engine."""
    types: Dict[str, Dict[str, str]] = field(default_factory=dict)       # TypeName -> {field: type}
    queries: Dict[str, str] = field(default_factory=dict)                 # queryName -> resolver_func
    mutations: Dict[str, str] = field(default_factory=dict)               # mutationName -> resolver_func
    raw: str = ""


@dataclass
class RBACBlock:
    """Fase 26 – Role-Based Access Control."""
    roles: List[str] = field(default_factory=list)                        # ['admin','user','guest']
    permissions: Dict[str, List[str]] = field(default_factory=dict)       # role -> [endpoint,...]
    default_role: str = "guest"
    raw: str = ""


@dataclass
class PagesBlock:
    routes: Dict[str, str] = field(default_factory=dict)


@dataclass
class SharedStateBlock:
    variables: Dict[str, str] = field(default_factory=dict)

@dataclass
class DatabaseBlock:
    provider: str = "sqlite"
    url:      str = "db.sqlite"
    settings: Dict[str, str] = field(default_factory=dict)

@dataclass
class DependenciesBlock:
    pip: List[str] = field(default_factory=list)
    npm: List[str] = field(default_factory=list)

@dataclass
class ServerBlock:
    raw:       str = ""
    imports:   List[str] = field(default_factory=list)
    functions: List["FuncDef"] = field(default_factory=list)

@dataclass
class FuncDef:
    name:   str
    params: List[str]
    body:   str
    param_types: Dict[str, str] = field(default_factory=dict)
    return_type: Optional[str] = None

@dataclass
class StateVar:
    name:    str
    setter:  str
    initial: str = "null"

@dataclass
class HandlerDef:
    name: str
    body: str

@dataclass
class EffectDef:
    body: str
    deps: str = "[]"


@dataclass
class RefVar:
    """use_ref(initial) → useRef(initial)"""
    name:    str
    initial: str = "null"


@dataclass
class MemoVar:
    """val = use_memo(def(): expr, [deps]) → useMemo(() => expr, deps)"""
    name:  str
    expr:  str
    deps:  str = "[]"


@dataclass
class CallbackVar:
    """fn = use_callback(def(): ..., [deps]) → useCallback(() => ..., deps)"""
    name:  str
    body:  str
    deps:  str = "[]"


@dataclass
class ReducerVar:
    """state, dispatch = use_reducer(reducer, initial) → useReducer(reducer, initial)"""
    state:    str
    dispatch: str
    reducer:  str
    initial:  str = "null"


@dataclass
class HookNode:
    """Custom React hook block: hook useName(): ..."""
    name:     str
    raw_body: str
    params:   List[str]       = field(default_factory=list)
    states:   List[StateVar]  = field(default_factory=list)
    effects:  List[EffectDef] = field(default_factory=list)
    handlers: List[HandlerDef] = field(default_factory=list)

@dataclass
class ComponentNode:
    name:      str
    params:    List[str]           = field(default_factory=list)
    states:    List[StateVar]      = field(default_factory=list)
    handlers:  List[HandlerDef]    = field(default_factory=list)
    effects:   List[EffectDef]     = field(default_factory=list)
    jsx:       str                 = ""
    raw_body:  str                 = ""
    refs:      List["RefVar"]      = field(default_factory=list)
    memos:     List["MemoVar"]     = field(default_factory=list)
    callbacks: List["CallbackVar"] = field(default_factory=list)
    reducers:  List["ReducerVar"]  = field(default_factory=list)

@dataclass
class StyleBlock:
    variables: Dict[str, str] = field(default_factory=dict)

@dataclass
class ModelNode:
    name:   str = ""
    source: str = ""
    kind:   str = "pytorch"


@dataclass
class AgentNode:
    name:     str
    raw_body: str
    settings: Dict[str, str] = field(default_factory=dict)


@dataclass
class PipelineNode:
    name:     str
    raw_body: str
    steps:    List[str] = field(default_factory=list)



# ── Parser ────────────────────────────────────────────────────────────────────

class ParseError(Exception):
    def __init__(self, message: str, line: int = 1, col: int = 1, suggestion: str = ""):
        super().__init__(message)
        self.line = line
        self.col = col
        self.suggestion = suggestion


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens
                       if t.type not in (TT.NEWLINE, TT.COMMENT)]
        self.pos = 0
        self._last_block_keyword: Optional[str] = None  # track context for suggestions

    def _cur(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token(TT.EOF, "", 0, 0)

    def _adv(self) -> Token:
        t = self._cur(); self.pos += 1; return t

    # ── friendly token names ─────────────────────────────────────────────────
    _FRIENDLY_NAMES = {
        TT.LBRACE: "'{'",
        TT.RBRACE: "'}'",
        TT.LPAREN: "'('",
        TT.RPAREN: "')'",
        TT.COLON: "':'",
        TT.COMMA: "','",
        TT.EQUALS: "'='",
        TT.IDENTIFIER: "a name",
        TT.STRING: "a string",
        TT.NUMBER: "a number",
        TT.BOOL: "True/False",
        TT.RAW_PYTHON: "block content",
        TT.SERVER: "'server'",
        TT.COMPONENT: "'component'",
        TT.STYLE: "'style'",
        TT.MODEL: "'model'",
        TT.DATABASE: "'database'",
        TT.DEPENDENCIES: "'dependencies'",
        TT.SHARED_STATE: "'shared_state'",
        TT.AGENT: "'agent'",
        TT.PIPELINE: "'pipeline'",
        TT.PAGES: "'pages'",
        TT.REALTIME: "'realtime'",
        TT.GRAPHQL: "'graphql'",
        TT.RBAC: "'rbac'",
        TT.WEBRTC: "'webrtc'",
        TT.MIDDLEWARE: "'middleware'",
        TT.EOF: "end of file",
    }

    # ── contextual suggestions based on what block we're parsing ──────────────
    _BLOCK_SUGGESTIONS = {
        "server":      "Server blocks use brace syntax: server { def my_func(): ... }",
        "component":   "Components use indent syntax: component MyName():  (with colon, not braces)",
        "style":       "Style blocks use brace syntax: style { primary = \"#2563eb\" }",
        "pages":       "Pages blocks use brace syntax: pages { Home = \"/\" }",
        "shared_state": "Shared state uses brace syntax: shared_state { count = 0 }",
        "database":    "Database blocks use brace syntax: database { provider = \"sqlite\" }",
        "dependencies": "Dependencies use brace syntax: dependencies { pip = [\"flask\"] }",
        "realtime":    "Realtime blocks use brace syntax: realtime { provider = \"websockets\" }",
        "graphql":     "GraphQL blocks use brace syntax: graphql { type User { ... } }",
        "rbac":        "RBAC blocks use brace syntax: rbac { roles = [...] }",
        "webrtc":      "WebRTC blocks use brace syntax: webrtc { signaling = \"websockets\" }",
        "middleware":  "Middleware blocks use brace syntax: middleware { def guard(req): ... }",
    }

    def _expect(self, *types) -> Token:
        t = self._cur()
        if t.type not in types:
            expected_friendly = " or ".join(
                self._FRIENDLY_NAMES.get(tt, tt.name) for tt in types
            )
            got_friendly = self._FRIENDLY_NAMES.get(t.type, t.value)
            msg = f"Expected {expected_friendly}, but got {got_friendly} ({t.value!r})"

            # Build contextual suggestion
            suggestion = ""
            if self._last_block_keyword:
                suggestion = self._BLOCK_SUGGESTIONS.get(self._last_block_keyword, "")

            # Specific common-mistake hints
            if t.type == TT.IDENTIFIER and t.value == "component" and TT.LBRACE in types:
                suggestion = "Components use indent syntax with colon: 'component Name():' NOT brace syntax 'component Name { }'"
            elif TT.LBRACE in types and t.type == TT.COLON:
                suggestion = f"Did you mean to use brace syntax? Try: {self._last_block_keyword or 'block'} {{ ... }}"
            elif TT.COLON in types and t.type == TT.LBRACE:
                suggestion = "Components use colon syntax, not braces: 'component Name():'"
            elif TT.RBRACE in types and t.type == TT.EOF:
                suggestion = "Unexpected end of file. Did you forget a closing '}' ?"
            elif TT.LBRACE in types and t.type == TT.EOF:
                suggestion = f"Unexpected end of file. Did you forget the opening '{{' after '{self._last_block_keyword or 'keyword'}'?"

            raise ParseError(msg, line=t.line, col=t.col, suggestion=suggestion)
        return self._adv()

    def _match(self, *types) -> bool:
        return self._cur().type in types

    # ── public ────────────────────────────────────────────────────────────────
    def parse(self) -> ProgramNode:
        prog = ProgramNode()
        while not self._match(TT.EOF):
            t = self._cur()
            if t.type == TT.SERVER:
                self._last_block_keyword = "server"
                prog.server = self._parse_server()
            elif t.type == TT.COMPONENT:
                self._last_block_keyword = "component"
                prog.components.append(self._parse_component())
            elif t.type == TT.STYLE:
                self._last_block_keyword = "style"
                prog.style = self._parse_style()
            elif t.type == TT.MODEL:
                self._last_block_keyword = "model"
                prog.models.append(self._parse_model())
            elif t.type == TT.DATABASE:
                self._last_block_keyword = "database"
                prog.database = self._parse_database()
            elif t.type == TT.DEPENDENCIES:
                self._last_block_keyword = "dependencies"
                prog.dependencies = self._parse_dependencies()
            elif t.type == TT.SHARED_STATE:
                self._last_block_keyword = "shared_state"
                prog.shared_state = self._parse_shared_state()
            elif t.type == TT.AGENT:
                self._last_block_keyword = "agent"
                prog.agents.append(self._parse_agent())
            elif t.type == TT.PIPELINE:
                self._last_block_keyword = "pipeline"
                prog.pipelines.append(self._parse_pipeline())
            elif t.type == TT.PAGES:
                self._last_block_keyword = "pages"
                prog.pages = self._parse_pages()
            elif t.type == TT.REALTIME:
                self._last_block_keyword = "realtime"
                prog.realtime = self._parse_realtime()
            elif t.type == TT.GRAPHQL:
                self._last_block_keyword = "graphql"
                prog.graphql = self._parse_graphql()
            elif t.type == TT.RBAC:
                self._last_block_keyword = "rbac"
                prog.rbac = self._parse_rbac()
            elif t.type == TT.WEBRTC:
                self._last_block_keyword = "webrtc"
                prog.webrtc = self._parse_webrtc()
            elif t.type == TT.MIDDLEWARE:
                self._last_block_keyword = "middleware"
                prog.middleware = self._parse_middleware()
            elif t.type == TT.LOCALE:
                self._last_block_keyword = "locale"
                prog.locale = self._parse_locale()
            else:
                # Unexpected token at top-level
                t = self._cur()
                msg = f"Token tingkat atas tidak valid: got {self._FRIENDLY_NAMES.get(t.type, t.value)} ({t.value!r})"
                suggestion = ""
                # Check for common casing mistakes
                val_lower = t.value.lower() if t.value else ""
                if val_lower in ("server", "component", "style", "database", "dependencies", "shared_state", "realtime", "graphql", "rbac", "webrtc", "middleware", "locale", "pages"):
                    suggestion = f"Di PyReact, keyword blok harus menggunakan huruf kecil (lowercase). Gunakan '{val_lower}' bukan '{t.value}'."
                else:
                    suggestion = f"Semua kode PyReact harus berada di dalam blok yang valid (seperti server {{ }}, component Name():, style {{ }}, dll.). Karakter/token '{t.value}' di luar blok tidak diperbolehkan."
                raise ParseError(msg, line=t.line, col=t.col, suggestion=suggestion)
        return prog


    # ── server ────────────────────────────────────────────────────────────────
    def _parse_server(self) -> ServerBlock:
        self._expect(TT.SERVER)
        self._expect(TT.LBRACE)
        raw_tok = self._cur()
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        sb = ServerBlock(raw=raw)
        self._analyse_server(sb, start_line=raw_tok.line)
        return sb

    def _analyse_server(self, sb: ServerBlock, start_line: int = 1):
        import ast
        import textwrap
        try:
            tree = ast.parse(textwrap.dedent(sb.raw))
        except Exception as e:
            if isinstance(e, SyntaxError):
                abs_line = start_line + (e.lineno or 1) - 1
                abs_col = e.offset or 1
                raise ParseError(
                    message=f"Kesalahan sintaksis Python di block server: {e.msg}",
                    line=abs_line,
                    col=abs_col,
                    suggestion="Pastikan kode Python di dalam block server memiliki sintaksis yang valid (misalnya kolon, tanda kurung, indentasi)."
                )
            self._analyse_server_fallback(sb)
            return

        sb.imports = []
        sb.functions = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                sb.imports.append(ast.unparse(node).strip())
            elif isinstance(node, ast.FunctionDef):
                params = []
                param_types = {}
                for arg in node.args.args:
                    params.append(arg.arg)
                    if arg.annotation:
                        param_types[arg.arg] = ast.unparse(arg.annotation).strip()
                
                return_type = None
                if node.returns:
                    return_type = ast.unparse(node.returns).strip()

                body_stmts = [ast.unparse(stmt) for stmt in node.body]
                body = "\n".join(body_stmts)

                func_def = FuncDef(
                    name=node.name,
                    params=params,
                    body=body,
                    param_types=param_types,
                    return_type=return_type
                )
                sb.functions.append(func_def)

    def _analyse_server_fallback(self, sb: ServerBlock):
        imp_re  = re.compile(r"^\s*((?:import|from)\s+.+)")
        func_re = re.compile(r"^\s*def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?\s*:")
        lines = sb.raw.splitlines()
        cur_func: Optional[FuncDef] = None
        body_lines: List[str] = []

        for line in lines:
            m = imp_re.match(line)
            if m:
                sb.imports.append(m.group(1).strip()); continue
            m = func_re.match(line)
            if m:
                if cur_func:
                    cur_func.body = "\n".join(body_lines)
                    sb.functions.append(cur_func)
                params_raw = m.group(2)
                params = []
                param_types = {}
                for p in params_raw.split(","):
                    p = p.strip()
                    if not p:
                        continue
                    if ":" in p:
                        p_name, p_type = p.split(":", 1)
                        p_name = p_name.strip()
                        params.append(p_name)
                        param_types[p_name] = p_type.strip()
                    else:
                        params.append(p)
                
                return_type = m.group(3).strip() if m.group(3) else None
                cur_func = FuncDef(
                    name=m.group(1),
                    params=params,
                    body="",
                    param_types=param_types,
                    return_type=return_type
                )
                body_lines = []; continue
            if cur_func:
                body_lines.append(line)

        if cur_func:
            cur_func.body = "\n".join(body_lines)
            sb.functions.append(cur_func)

    # ── component ─────────────────────────────────────────────────────────────
    def _parse_component(self) -> ComponentNode:
        self._expect(TT.COMPONENT)
        name = self._expect(TT.IDENTIFIER).value
        params: List[str] = []
        if self._match(TT.LPAREN):
            self._adv()
            while not self._match(TT.RPAREN, TT.EOF):
                if self._match(TT.IDENTIFIER):
                    params.append(self._adv().value)
                else:
                    self._adv()
            self._expect(TT.RPAREN)
        if self._match(TT.COLON):
            self._adv()
        self._expect(TT.LBRACE)

        # collect raw body until matching RBRACE
        raw_body = ""
        if self._match(TT.RAW_PYTHON):
            raw_body = self._adv().value
        else:
            parts, depth = [], 1
            while not self._match(TT.EOF):
                t = self._cur()
                if t.type == TT.LBRACE: depth += 1
                elif t.type == TT.RBRACE:
                    depth -= 1
                    if depth == 0: break
                parts.append(t.value)
                self._adv()
            raw_body = " ".join(parts)

        self._expect(TT.RBRACE)
        node = ComponentNode(name=name, params=params, raw_body=raw_body)
        self._analyse_component(node, raw_body)
        return node

    def _analyse_component(self, node: ComponentNode, raw: str):
        # use_ref: ref = use_ref(initial)
        for m in re.finditer(r"(\w+)\s*=\s*use_ref\s*\(([^)]*)\)", raw):
            node.refs.append(RefVar(m.group(1), m.group(2).strip() or "null"))

        # use_memo: name = use_memo(def(): expr, [deps])
        for m in re.finditer(
            r"(\w+)\s*=\s*use_memo\s*\(\s*def\s*\(\s*\)\s*:\s*([^,]+?)\s*,\s*(\[[^\]]*\])\s*\)",
            raw, re.DOTALL
        ):
            node.memos.append(MemoVar(m.group(1), m.group(2).strip(), m.group(3).strip()))

        # use_callback: name = use_callback(def(): ..., [deps])
        for m in re.finditer(
            r"(\w+)\s*=\s*use_callback\s*\(\s*def\s*\(\s*\)\s*:([^,]+?)\s*,\s*(\[[^\]]*\])\s*\)",
            raw, re.DOTALL
        ):
            node.callbacks.append(CallbackVar(m.group(1), m.group(2).strip(), m.group(3).strip()))

        # use_reducer: state, dispatch = use_reducer(reducer_fn, initial)
        for m in re.finditer(
            r"(\w+)\s*,\s*(\w+)\s*=\s*use_reducer\s*\(\s*([\w]+)\s*,\s*([^)]+)\)",
            raw
        ):
            node.reducers.append(ReducerVar(
                state=m.group(1), dispatch=m.group(2),
                reducer=m.group(3), initial=m.group(4).strip()
            ))

        # state vars
        for m in re.finditer(r"(\w+)\s*,\s*(\w+)\s*=\s*use_state\s*\(([^)]*)\)", raw):
            node.states.append(StateVar(m.group(1), m.group(2), m.group(3).strip() or "null"))

        # use_effect detection: use_effect(def(): ..., [deps]) or use_effect(def(): ...)
        for m in re.finditer(
            r"use_effect\s*\(\s*def\s*\(\s*\)\s*:([^,]+?)(?:,\s*(\[[^\]]*\]))?\s*\)",
            raw, re.DOTALL
        ):
            body = m.group(1).strip()
            deps = m.group(2).strip() if m.group(2) else "[]"
            node.effects.append(EffectDef(body=body, deps=deps))

        # handlers: parse line-by-line to get individual def blocks
        lines = raw.splitlines()
        func_re = re.compile(r"^\s{0,4}def\s+(\w+)\s*\([^)]*\)\s*:")
        in_func: Optional[str] = None
        func_lines: List[str] = []
        in_jsx = False
        jsx_lines: List[str] = []
        paren_depth = 0

        for line in lines:
            stripped = line.strip()

            # detect return ( start
            if not in_jsx and re.match(r"^\s*return\s*\(", line):
                in_jsx = True
                paren_depth = line.count("(") - line.count(")")
                # capture content after "return ("
                m = re.match(r"^\s*return\s*\((.*)", line)
                if m:
                    jsx_lines.append(m.group(1))
                # save current func if any
                if in_func:
                    node.handlers.append(HandlerDef(in_func, "\n".join(func_lines)))
                    in_func = None; func_lines = []
                continue

            if in_jsx:
                paren_depth += line.count("(") - line.count(")")
                if paren_depth <= 0:
                    # last line might have closing ) — strip it
                    last = line.rstrip()
                    if last.endswith(")"):
                        last = last[:-1]
                    if last.strip():
                        jsx_lines.append(last)
                    node.jsx = "\n".join(jsx_lines).strip()
                    in_jsx = False
                else:
                    jsx_lines.append(line)
                continue

            m = func_re.match(line)
            if m:
                if in_func:
                    node.handlers.append(HandlerDef(in_func, "\n".join(func_lines)))
                in_func = m.group(1)
                func_lines = []
                continue

            if in_func:
                # check for next top-level statement (non-indented, non-blank)
                if stripped and not line.startswith("    ") and not line.startswith("\t"):
                    node.handlers.append(HandlerDef(in_func, "\n".join(func_lines)))
                    in_func = None; func_lines = []
                else:
                    func_lines.append(line)

        if in_func:
            node.handlers.append(HandlerDef(in_func, "\n".join(func_lines)))


    # ── style ─────────────────────────────────────────────────────────────────
    def _parse_style(self) -> StyleBlock:
        self._expect(TT.STYLE)
        self._expect(TT.LBRACE)
        raw = self._adv().value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        sb = StyleBlock()
        for m in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+)["\']', raw):
            sb.variables[m.group(1)] = m.group(2)
        return sb

    # ── model ─────────────────────────────────────────────────────────────────
    def _parse_model(self) -> ModelNode:
        self._expect(TT.MODEL)
        name = self._expect(TT.IDENTIFIER).value
        if self._match(TT.COLON): self._adv()
        self._expect(TT.LBRACE)
        raw = self._adv().value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        node = ModelNode(name=name)
        m = re.search(r'source\s*=\s*["\']([^"\']+)', raw)
        if m: node.source = m.group(1)
        m = re.search(r'type\s*=\s*["\']([^"\']+)', raw)
        if m: node.kind = m.group(1)
        return node

    # ── database ──────────────────────────────────────────────────────────────
    def _parse_database(self) -> DatabaseBlock:
        self._expect(TT.DATABASE)
        self._expect(TT.LBRACE)
        raw = self._adv().value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        db = DatabaseBlock()
        for m in re.finditer(r'(\w+)\s*=\s*["\']([^"\']+)["\']', raw):
            key, val = m.group(1), m.group(2)
            if key == "provider":
                db.provider = val
            elif key == "url":
                db.url = val
            else:
                db.settings[key] = val
        return db

    # ── dependencies ──────────────────────────────────────────────────────────
    def _parse_dependencies(self) -> DependenciesBlock:
        self._expect(TT.DEPENDENCIES)
        self._expect(TT.LBRACE)
        raw = self._adv().value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        dep = DependenciesBlock()
        pip_match = re.search(r'pip\s*=\s*\[(.*?)\]', raw, re.DOTALL)
        if pip_match:
            items = re.findall(r'["\']([^"\']+)["\']', pip_match.group(1))
            dep.pip = [item.strip() for item in items]
        npm_match = re.search(r'npm\s*=\s*\[(.*?)\]', raw, re.DOTALL)
        if npm_match:
            items = re.findall(r'["\']([^"\']+)["\']', npm_match.group(1))
            dep.npm = [item.strip() for item in items]
        return dep

    # ── shared_state ──────────────────────────────────────────────────────────
    def _parse_shared_state(self) -> SharedStateBlock:
        self._expect(TT.SHARED_STATE)
        self._expect(TT.LBRACE)
        raw = self._adv().value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        sb = SharedStateBlock()
        for m in re.finditer(r'(\w+)\s*=\s*(.+)', raw):
            name = m.group(1).strip()
            expr = m.group(2).strip()
            expr = re.split(r'[#\n]', expr)[0].strip()
            if expr.endswith(','):
                expr = expr[:-1].strip()
            sb.variables[name] = expr
        return sb

    # ── agent ─────────────────────────────────────────────────────────────────
    def _parse_agent(self) -> AgentNode:
        self._expect(TT.AGENT)
        name = self._expect(TT.IDENTIFIER).value
        self._expect(TT.LBRACE)
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)

        settings = {}
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                settings[k.strip()] = v.strip().strip("'\"")
        return AgentNode(name=name, raw_body=raw, settings=settings)

    # ── pipeline ──────────────────────────────────────────────────────────────
    def _parse_pipeline(self) -> PipelineNode:
        self._expect(TT.PIPELINE)
        name = self._expect(TT.IDENTIFIER).value
        self._expect(TT.LBRACE)
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)

        steps = []
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                if k.strip() == "steps":
                    v_clean = v.strip().lstrip("[").rstrip("]")
                    steps = [s.strip() for s in v_clean.split(",") if s.strip()]
        return PipelineNode(name=name, raw_body=raw, steps=steps)

    # ── pages ─────────────────────────────────────────────────────────────────
    def _parse_pages(self) -> PagesBlock:
        self._expect(TT.PAGES)
        self._expect(TT.LBRACE)
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        pb = PagesBlock()
        # Simpan SELURUH meta string (termasuk [guard], [layout=X])
        # agar router.py bisa parsing lebih lanjut
        # Pola: ComponentName = "/path" [opsi opsional]
        for m in re.finditer(r'(\w+)\s*=\s*(.+)', raw):
            name = m.group(1).strip()
            expr = m.group(2).strip()
            # Ambil sampai newline atau komentar, tapi pertahankan [...]
            expr = expr.split('#')[0].strip()
            if expr.endswith(','):
                expr = expr[:-1].strip()
            pb.routes[name] = expr   # simpan raw: '"/" [guard]' atau '"/about"'
        return pb

    # ── realtime ──────────────────────────────────────────────────────────────
    def _parse_realtime(self) -> RealtimeBlock:
        self._expect(TT.REALTIME)
        self._expect(TT.LBRACE)
        raw_tok = self._cur()
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        rb = RealtimeBlock(raw=raw)
        self._analyse_realtime(rb, start_line=raw_tok.line)
        return rb

    def _analyse_realtime(self, rb: RealtimeBlock, start_line: int = 1):
        import ast
        import textwrap
        try:
            tree = ast.parse(textwrap.dedent(rb.raw))
        except Exception as e:
            if isinstance(e, SyntaxError):
                abs_line = start_line + (e.lineno or 1) - 1
                abs_col = e.offset or 1
                raise ParseError(
                    message=f"Kesalahan sintaksis Python di block realtime: {e.msg}",
                    line=abs_line,
                    col=abs_col,
                    suggestion="Pastikan kode Python di dalam block realtime memiliki sintaksis yang valid."
                )
            # basic regex fallback
            lines = rb.raw.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("provider"):
                    m = re.search(r'provider\s*=\s*["\']([^"\']+)["\']', line)
                    if m:
                        rb.provider = m.group(1)
                elif line.startswith("channels"):
                    m = re.search(r'channels\s*=\s*\[(.*?)\]', line)
                    if m:
                        rb.channels = [c.strip().strip('"').strip("'") for c in m.group(1).split(",") if c.strip()]
            return

        rb.functions = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "provider":
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                rb.provider = node.value.value
                            elif isinstance(node.value, ast.Str):
                                rb.provider = node.value.s
                        elif target.id == "channels":
                            if isinstance(node.value, ast.List):
                                rb.channels = []
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Constant):
                                        rb.channels.append(str(elt.value))
                                    elif isinstance(elt, ast.Str):
                                        rb.channels.append(elt.s)
            elif isinstance(node, ast.FunctionDef):
                params = [arg.arg for arg in node.args.args]
                body = "\n".join(ast.unparse(stmt) for stmt in node.body)
                rb.functions.append(FuncDef(name=node.name, params=params, body=body))


    # ── graphql ───────────────────────────────────────────────────────────────
    def _parse_graphql(self) -> "GraphQLBlock":
        self._expect(TT.GRAPHQL)
        self._expect(TT.LBRACE)
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        from .parser import GraphQLBlock
        gb = GraphQLBlock(raw=raw)

        # Parse type definitions: type TypeName { field: Type }
        for tm in re.finditer(
            r'type\s+(\w+)\s*\{([^}]*)\}', raw, re.DOTALL
        ):
            type_name = tm.group(1)
            fields_raw = tm.group(2)
            fields: Dict[str, str] = {}
            for fm in re.finditer(r'(\w+)\s*:\s*([\w!\[\]]+)', fields_raw):
                fields[fm.group(1)] = fm.group(2)
            gb.types[type_name] = fields

        # Parse Query resolvers: query queryName -> resolver_func
        for qm in re.finditer(r'query\s+(\w+)\s*->\s*(\w+)', raw):
            gb.queries[qm.group(1)] = qm.group(2)

        # Parse Mutation resolvers: mutation mutationName -> resolver_func
        for mm in re.finditer(r'mutation\s+(\w+)\s*->\s*(\w+)', raw):
            gb.mutations[mm.group(1)] = mm.group(2)

        return gb

    # ── rbac ──────────────────────────────────────────────────────────────────
    def _parse_rbac(self) -> "RBACBlock":
        self._expect(TT.RBAC)
        self._expect(TT.LBRACE)
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        from .parser import RBACBlock
        rb = RBACBlock(raw=raw)

        # roles = ["admin", "user", "guest"]
        roles_m = re.search(r'roles\s*=\s*\[(.*?)\]', raw, re.DOTALL)
        if roles_m:
            rb.roles = [
                r.strip().strip("'\"")
                for r in roles_m.group(1).split(",")
                if r.strip()
            ]

        # default_role = "guest"
        dr_m = re.search(r'default_role\s*=\s*["\'](\w+)["\']', raw)
        if dr_m:
            rb.default_role = dr_m.group(1)

        # permissions: role -> ["endpoint1", "endpoint2"]
        for pm in re.finditer(r'(\w+)\s*:\s*\[(.*?)\]', raw, re.DOTALL):
            role = pm.group(1).strip()
            if role in ("roles", "permissions"):
                continue
            endpoints = [
                e.strip().strip("'\"")
                for e in pm.group(2).split(",")
                if e.strip()
            ]
            if endpoints:
                rb.permissions[role] = endpoints

        return rb

    # ── webrtc ────────────────────────────────────────────────────────────────
    def _parse_webrtc(self) -> "WebRTCBlock":
        self._expect(TT.WEBRTC)
        self._expect(TT.LBRACE)
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        from .parser import WebRTCBlock
        wb = WebRTCBlock(raw=raw)

        # signaling = "websockets"
        sig_m = re.search(r'signaling\s*=\s*["\'](\w+)["\']', raw)
        if sig_m:
            wb.signaling = sig_m.group(1)

        # codecs = ["vp8", "opus"]
        codecs_m = re.search(r'codecs\s*=\s*\[(.*?)\]', raw, re.DOTALL)
        if codecs_m:
            wb.codecs = [
                c.strip().strip("'\"")
                for c in codecs_m.group(1).split(",")
                if c.strip()
            ]

        return wb

    # ── middleware ──────────────────────────────────────────────────────────
    def _parse_middleware(self) -> "MiddlewareBlock":
        self._expect(TT.MIDDLEWARE)
        self._expect(TT.LBRACE)
        raw_tok = self._cur()
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        from .parser import MiddlewareBlock
        mb = MiddlewareBlock(raw=raw)

        # Parse middleware functions using same approach as server
        import ast as _ast
        import textwrap
        try:
            tree = _ast.parse(textwrap.dedent(raw))
            for node in tree.body:
                if isinstance(node, _ast.FunctionDef):
                    params = [arg.arg for arg in node.args.args]
                    body = "\n".join(_ast.unparse(stmt) for stmt in node.body)
                    mb.functions.append(FuncDef(name=node.name, params=params, body=body))
        except Exception as e:
            if isinstance(e, SyntaxError):
                abs_line = raw_tok.line + (e.lineno or 1) - 1
                abs_col = e.offset or 1
                raise ParseError(
                    message=f"Kesalahan sintaksis Python di block middleware: {e.msg}",
                    line=abs_line,
                    col=abs_col,
                    suggestion="Pastikan kode Python di dalam block middleware memiliki sintaksis yang valid."
                )
            # Fallback: regex
            func_re = re.compile(r"^\s*def\s+(\w+)\s*\(([^)]*)\)\s*:", re.MULTILINE)
            for m in func_re.finditer(raw):
                mb.functions.append(FuncDef(name=m.group(1), params=[m.group(2).strip()], body=""))

        return mb

    # ── locale (i18n) ─────────────────────────────────────────────────────
    def _parse_locale(self) -> "LocaleBlock":
        """Parse locale { } block for i18n support."""
        self._expect(TT.LOCALE)
        self._expect(TT.LBRACE)
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        
        lb = LocaleBlock(raw=raw)
        
        # Parse default language
        default_m = re.search(r'default\s*=\s*["\']([^"\']+)["\']', raw)
        if default_m:
            lb.default = default_m.group(1)
        
        # Parse supported languages list
        supported_m = re.search(r'supported\s*=\s*\[(.*?)\]', raw, re.DOTALL)
        if supported_m:
            lb.supported = [
                lang.strip().strip("'\"")
                for lang in supported_m.group(1).split(",")
                if lang.strip()
            ]
        
        # Parse translation keys
        # Format: key = { lang = "value", lang2 = "value2" }
        trans_re = re.compile(
            r'(\w+)\s*=\s*\{([^}]+)\}',
            re.MULTILINE
        )
        for m in trans_re.finditer(raw):
            key = m.group(1)
            if key in ("default", "supported"):
                continue  # Skip config keys
            
            translations_block = m.group(2)
            lang_values = {}
            
            # Parse lang = "value" pairs
            lang_re = re.compile(r'(\w+)\s*=\s*["\']([^"\']*)["\']')
            for lang_m in lang_re.finditer(translations_block):
                lang_code = lang_m.group(1)
                value = lang_m.group(2)
                lang_values[lang_code] = value
            
            if lang_values:
                lb.translations[key] = lang_values
        
        return lb
