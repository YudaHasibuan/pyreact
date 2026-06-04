"""PYREACT Router Code Generator — Fase 16
File-System Routing & Nested Page Blocks.

Fitur:
  - pages { } block: routing eksplisit dengan guards, layout, params
  - File-system routing: scan folder pages/ otomatis (Next.js style)
  - Nested routes: pages bersarang dengan layout parent
  - Dynamic segments: [id].pyreact -> /route/:id
  - Route guards: auth-protected routes
  - react-router-dom v6 BrowserRouter + lazy imports
  - 404 fallback + loading suspense
  - Link helper: <UI.Link> component
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class RouteEntry:
    """Satu entri route yang sudah dinormalisasi."""
    path:        str               # URL path, mis: "/", "/about", "/user/:id"
    component:   str               # Nama komponen React, mis: "Home", "UserDetail"
    layout:      Optional[str] = None   # Nama layout komponen pembungkus
    guard:       bool          = False  # True jika perlu autentikasi
    exact:       bool          = True
    children:    List["RouteEntry"] = field(default_factory=list)
    source_file: Optional[str] = None   # Asal file (untuk file-system routing)


@dataclass
class RouterConfig:
    """Konfigurasi router lengkap yang akan di-generate ke React."""
    routes:          List[RouteEntry]
    has_nested:      bool = False
    has_guards:      bool = False
    has_dynamic:     bool = False
    default_layout:  Optional[str] = None
    not_found_comp:  Optional[str] = None   # Komponen 404 kustom


# ── Route parsers ─────────────────────────────────────────────────────────────

def parse_pages_block(raw_routes: Dict[str, str]) -> RouterConfig:
    """
    Parsing pages block dari parser AST.

    Sintaks yang didukung:
        pages {
            Home     = "/"
            About    = "/about"
            UserDetail = "/user/:id"
            Dashboard = "/dashboard" [guard]
            Settings  = "/settings"  [guard, layout=DashLayout]
        }
    """
    routes: List[RouteEntry] = []
    has_guards = False
    has_dynamic = False

    for comp_name, meta in raw_routes.items():
        # Pisahkan path dan opsi seperti [guard], [layout=X]
        path, options = _parse_route_meta(meta)

        guard  = "guard" in options
        layout = options.get("layout")

        if guard:
            has_guards = True
        if ":" in path or "[" in path:
            has_dynamic = True

        routes.append(RouteEntry(
            path=path,
            component=comp_name,
            layout=layout,
            guard=guard,
        ))

    has_nested = any(r.layout for r in routes)
    return RouterConfig(
        routes=routes,
        has_nested=has_nested,
        has_guards=has_guards,
        has_dynamic=has_dynamic,
    )


def _parse_route_meta(raw_value: str) -> Tuple[str, Dict]:
    """
    Parse nilai route dari pages block.
    Contoh: '"/dashboard" [guard, layout=AppLayout]'
    Kembalikan (path_str, options_dict).
    """
    options: Dict = {}
    # Ambil path string
    path_match = re.search(r'["\']([^"\']+)["\']', raw_value)
    path = path_match.group(1) if path_match else raw_value.strip()

    # Ambil opsi dalam bracket [...]
    opts_match = re.search(r'\[([^\]]+)\]', raw_value)
    if opts_match:
        for part in opts_match.group(1).split(","):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                options[k.strip()] = v.strip()
            else:
                options[part] = True

    return path, options


def scan_pages_folder(project_root: str) -> Optional[RouterConfig]:
    """
    File-System Routing: scan folder pages/ dalam project_root.

    Konvensi penamaan file (mirip Next.js):
        pages/index.pyreact          -> /
        pages/about.pyreact          -> /about
        pages/user/[id].pyreact      -> /user/:id
        pages/blog/index.pyreact     -> /blog
        pages/blog/[slug].pyreact    -> /blog/:slug
        pages/dashboard/index.pyreact -> /dashboard  (+ auto guard jika ada _layout)
        pages/_layout.pyreact        -> Layout wrapper (tidak di-route)
        pages/404.pyreact            -> Not Found page
    """
    pages_dir = Path(project_root) / "pages"
    if not pages_dir.exists():
        return None

    routes: List[RouteEntry] = []
    has_dynamic = False
    not_found   = None

    for pyreact_file in sorted(pages_dir.rglob("*.pyreact")):
        rel = pyreact_file.relative_to(pages_dir)
        parts = list(rel.parts)
        filename = parts[-1].replace(".pyreact", "")

        # Skip layout files
        if filename.startswith("_"):
            continue

        # Not Found page
        if filename == "404":
            not_found = "NotFound"
            routes.append(RouteEntry(
                path="*",
                component="NotFound",
                source_file=str(pyreact_file),
            ))
            continue

        # Bangun URL path
        url_parts = []
        for p in parts[:-1]:               # direktori
            url_parts.append(_to_url_segment(p))
        if filename != "index":
            url_parts.append(_to_url_segment(filename))

        url_path = "/" + "/".join(url_parts) if url_parts else "/"

        if ":" in url_path:
            has_dynamic = True

        # Nama komponen: PascalCase dari path
        comp_name = _to_component_name(parts)

        routes.append(RouteEntry(
            path=url_path,
            component=comp_name,
            source_file=str(pyreact_file),
        ))

    if not routes:
        return None

    return RouterConfig(
        routes=routes,
        has_nested=False,
        has_guards=False,
        has_dynamic=has_dynamic,
        not_found_comp=not_found,
    )


def _to_url_segment(name: str) -> str:
    """Konversi nama file ke URL segment. [id] -> :id"""
    m = re.match(r'^\[(.+)\]$', name)
    if m:
        return f":{m.group(1)}"
    return name.lower().replace("_", "-")


def _to_component_name(parts: List[str]) -> str:
    """Buat nama komponen PascalCase dari path parts."""
    segments = []
    for p in parts:
        p = p.replace(".pyreact", "").replace("[", "").replace("]", "")
        segments.append(p.capitalize())
    name = "".join(segments)
    if name.endswith("Index"):
        name = name[:-5] or "Index"
    return name or "Home"


# ── React Router DOM code generator ───────────────────────────────────────────

class RouterCodeGenerator:
    """
    Menghasilkan kode React menggunakan react-router-dom v6.
    """

    def __init__(self, config: RouterConfig, components: List[str]):
        self.config     = config
        self.components = components   # Daftar nama komponen yang ada di project

    def generate_app_jsx(self, has_database: bool = False,
                         has_shared_state: bool = False) -> str:
        """
        Generate file App.jsx lengkap dengan react-router-dom v6.
        """
        lines: List[str] = []

        # ── Imports ────────────────────────────────────────────────────────────
        lines += [
            'import React, { useState, useEffect, Suspense } from "react";',
            'import { BrowserRouter, Routes, Route, Navigate, useNavigate, useParams, useLocation, Link } from "react-router-dom";',
            'import { UI } from "./ui/components";',
            'import { server } from "./pybridge";',
        ]
        if has_shared_state:
            lines.append('import { useSharedState } from "./store";')
        if has_database:
            lines.append('const AdminConsole = React.lazy(() => import("./ui/Admin"));')
        lines.append("")

        # ── Lazy imports untuk setiap komponen ────────────────────────────────
        imported_comps = set()
        for route in self.config.routes:
            if route.component not in imported_comps and route.path != "*":
                lines.append(
                    f'const {route.component} = React.lazy(() => import("./{route.component}"));'
                )
                imported_comps.add(route.component)

        # Not Found komponen
        if self.config.not_found_comp and "NotFound" not in imported_comps:
            lines.append('const NotFound = React.lazy(() => import("./NotFound"));')
        lines.append("")

        # ── Loading fallback ───────────────────────────────────────────────────
        lines += [
            "const PageLoader = () => (",
            '  <div className="min-h-screen flex items-center justify-center bg-[#090d16]">',
            '    <div className="flex flex-col items-center gap-4">',
            '      <div className="w-10 h-10 border-2 border-white/20 border-t-blue-500 rounded-full animate-spin" />',
            '      <span className="text-gray-400 text-sm">Loading...</span>',
            "    </div>",
            "  </div>",
            ");",
            "",
        ]

        # ── RouteGuard (jika ada protected routes) ─────────────────────────────
        if self.config.has_guards:
            lines += self._gen_route_guard()

        # ── Navigate helper (window.navigate) ─────────────────────────────────
        lines += [
            "// Global navigate helper — gunakan navigate('/path') dari mana saja",
            "let _navigate = null;",
            "export const navigate = (to) => _navigate && _navigate(to);",
            "",
            "function NavigateCapture() {",
            "  _navigate = useNavigate();",
            "  return null;",
            "}",
            "",
        ]

        # ── Main App component ─────────────────────────────────────────────────
        lines.append("export default function App() {")
        lines.append("  return (")
        lines.append("    <BrowserRouter>")
        lines.append("      <NavigateCapture />")
        lines.append(f"      <Suspense fallback={{<PageLoader />}}>")
        lines.append("        <Routes>")

        if has_database:
            lines.append('          <Route path="/admin" element={<AdminConsole />} />')

        # ── Render routes ──────────────────────────────────────────────────────
        self._append_routes(lines, self.config.routes, indent="          ")

        # Default 404 jika tidak ada not_found_comp
        if not self.config.not_found_comp:
            lines.append(
                '          <Route path="*" element={'
                '<div className="min-h-screen bg-[#070b13] text-white flex flex-col items-center '
                'justify-center gap-4">'
                '<h1 className="text-6xl font-bold text-white/20">404</h1>'
                '<p className="text-gray-400">Halaman tidak ditemukan.</p>'
                '<a href="/" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-xl text-sm '
                'font-semibold transition text-white">Kembali ke Home</a>'
                "</div>} />"
            )

        lines += [
            "        </Routes>",
            "      </Suspense>",
            "    </BrowserRouter>",
            "  );",
            "}",
        ]

        return "\n".join(lines) + "\n"

    def _append_routes(self, lines: List[str], routes: List[RouteEntry],
                       indent: str = "          ") -> None:
        """Rekursif append route JSX ke lines."""
        for route in routes:
            if route.path == "*":
                # Wildcard / 404
                if self.config.not_found_comp:
                    lines.append(
                        f'{indent}<Route path="*" element={{<{route.component} />}} />'
                    )
                continue

            element = self._wrap_element(route)

            if route.children:
                lines.append(f'{indent}<Route path="{route.path}" element={{{element}}}>',)
                self._append_routes(lines, route.children, indent + "  ")
                lines.append(f"{indent}</Route>")
            else:
                lines.append(
                    f'{indent}<Route path="{route.path}" element={{{element}}} />'
                )

    def _wrap_element(self, route: RouteEntry) -> str:
        """Bungkus komponen dengan guard/layout jika diperlukan."""
        comp = f"<{route.component} />"
        if route.guard and self.config.has_guards:
            comp = f"<RequireAuth>{comp}</RequireAuth>"
        if route.layout:
            comp = f"<{route.layout}>{comp}</{route.layout}>"
        return comp

    def _gen_route_guard(self) -> List[str]:
        """Generate komponen RequireAuth untuk protected routes."""
        return [
            "// Route Guard — redirect ke /login jika belum terautentikasi",
            "function RequireAuth({ children }) {",
            "  const token = localStorage.getItem('pyreact_token')",
            "             || sessionStorage.getItem('pyreact_token');",
            "  const location = useLocation();",
            "  if (!token) {",
            '    return <Navigate to="/login" state={{ from: location }} replace />;',
            "  }",
            "  return children;",
            "}",
            "",
        ]

    def generate_ui_link_component(self) -> str:
        """
        Tambahkan UI.Link dan UI.NavLink ke komponen UI.
        Ini akan di-inject ke UI_COMPONENTS_JSX.
        """
        return """\
  Link: ({ to, children, className = "", ...props }) => (
    <a
      href={to}
      onClick={(e) => {
        e.preventDefault();
        window.history.pushState(null, "", to);
        window.dispatchEvent(new PopStateEvent("popstate"));
      }}
      className={className}
      {...props}
    >
      {children}
    </a>
  ),
  NavLink: ({ to, children, activeClass = "text-blue-400 border-b-2 border-blue-500", className = "" }) => {
    const active = window.location.pathname === to;
    return (
      <a
        href={to}
        onClick={(e) => {
          e.preventDefault();
          window.history.pushState(null, "", to);
          window.dispatchEvent(new PopStateEvent("popstate"));
        }}
        className={`${className} ${active ? activeClass : ""} transition`}
      >
        {children}
      </a>
    );
  },
"""


# ── File-system route scanner for compiler pipeline ────────────────────────────

def build_router_config(ast, project_root: str = ".") -> Optional[RouterConfig]:
    """
    Bangun RouterConfig dari AST atau file-system scan.
    Prioritas: pages block > file-system scan.
    """
    # 1. Gunakan pages block jika ada
    if ast.pages and ast.pages.routes:
        return parse_pages_block(ast.pages.routes)

    # 2. File-system routing fallback
    fs_config = scan_pages_folder(project_root)
    if fs_config:
        return fs_config

    return None


# ── Package.json updater ───────────────────────────────────────────────────────

ROUTER_NPM_DEPS = {
    "react-router-dom": "^6.22.0",
}

def inject_router_deps(package_json_str: str) -> str:
    """
    Inject react-router-dom ke dalam string package.json.
    """
    import json
    try:
        pkg = json.loads(package_json_str)
        deps = pkg.setdefault("dependencies", {})
        for k, v in ROUTER_NPM_DEPS.items():
            if k not in deps:
                deps[k] = v
        return json.dumps(pkg, indent=2)
    except Exception:
        # Fallback: inject langsung dengan string replace
        inject = ',\n    "react-router-dom": "^6.22.0"'
        return package_json_str.replace(
            '"react": "^18', '"react-router-dom": "^6.22.0",\n    "react": "^18'
        )
