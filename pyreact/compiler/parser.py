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
class ComponentNode:
    name:      str
    params:    List[str]           = field(default_factory=list)
    states:    List[StateVar]      = field(default_factory=list)
    handlers:  List[HandlerDef]    = field(default_factory=list)
    jsx:       str                 = ""
    raw_body:  str                 = ""

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
    def __init__(self, message: str, line: int = 1, col: int = 1):
        super().__init__(message)
        self.line = line
        self.col = col


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens
                       if t.type not in (TT.NEWLINE, TT.COMMENT)]
        self.pos = 0

    def _cur(self) -> Token:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else Token(TT.EOF, "", 0, 0)

    def _adv(self) -> Token:
        t = self._cur(); self.pos += 1; return t

    def _expect(self, *types) -> Token:
        t = self._cur()
        if t.type not in types:
            expected_names = ", ".join(tt.name for tt in types)
            raise ParseError(
                f"Expected {expected_names}, got {t.type.name} {t.value!r}",
                line=t.line,
                col=t.col
            )
        return self._adv()

    def _match(self, *types) -> bool:
        return self._cur().type in types

    # ── public ────────────────────────────────────────────────────────────────
    def parse(self) -> ProgramNode:
        prog = ProgramNode()
        while not self._match(TT.EOF):
            t = self._cur()
            if t.type == TT.SERVER:
                prog.server = self._parse_server()
            elif t.type == TT.COMPONENT:
                prog.components.append(self._parse_component())
            elif t.type == TT.STYLE:
                prog.style = self._parse_style()
            elif t.type == TT.MODEL:
                prog.models.append(self._parse_model())
            elif t.type == TT.DATABASE:
                prog.database = self._parse_database()
            elif t.type == TT.DEPENDENCIES:
                prog.dependencies = self._parse_dependencies()
            elif t.type == TT.SHARED_STATE:
                prog.shared_state = self._parse_shared_state()
            elif t.type == TT.AGENT:
                prog.agents.append(self._parse_agent())
            elif t.type == TT.PIPELINE:
                prog.pipelines.append(self._parse_pipeline())
            elif t.type == TT.PAGES:
                prog.pages = self._parse_pages()
            elif t.type == TT.REALTIME:
                prog.realtime = self._parse_realtime()
            elif t.type == TT.GRAPHQL:
                prog.graphql = self._parse_graphql()
            elif t.type == TT.RBAC:
                prog.rbac = self._parse_rbac()
            elif t.type == TT.WEBRTC:
                prog.webrtc = self._parse_webrtc()
            else:
                self._adv()
        return prog


    # ── server ────────────────────────────────────────────────────────────────
    def _parse_server(self) -> ServerBlock:
        self._expect(TT.SERVER)
        self._expect(TT.LBRACE)
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        sb = ServerBlock(raw=raw)
        self._analyse_server(sb)
        return sb

    def _analyse_server(self, sb: ServerBlock):
        import ast
        import textwrap
        try:
            tree = ast.parse(textwrap.dedent(sb.raw))
        except Exception:
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
        # state vars
        for m in re.finditer(r"(\w+)\s*,\s*(\w+)\s*=\s*use_state\s*\(([^)]*)\)", raw):
            node.states.append(StateVar(m.group(1), m.group(2), m.group(3).strip() or "null"))

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
        raw = self._expect(TT.RAW_PYTHON).value if self._match(TT.RAW_PYTHON) else ""
        self._expect(TT.RBRACE)
        rb = RealtimeBlock(raw=raw)
        self._analyse_realtime(rb)
        return rb

    def _analyse_realtime(self, rb: RealtimeBlock):
        import ast
        import textwrap
        try:
            tree = ast.parse(textwrap.dedent(rb.raw))
        except Exception:
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

