# Product Requirement Document (PRD): PyReact v1.2

**Status:** Updated | **Version:** 1.2.0 | **Author:** Yuda Hasibuan | **Date:** 4 Juni 2026

---

## 1. Executive Summary & Vision

### 1.1 Latar Belakang

Pengembangan aplikasi web modern saat ini sangat terfragmentasi. Developer harus membagi logika aplikasi ke dalam dua dunia berbeda: Backend (Python/Flask/FastAPI) dan Frontend (JavaScript/React/Vite). Hal ini melahirkan kompleksitas boilerplate API, penanganan CORS, sinkronisasi skema data, konfigurasi bundler (Vite/Webpack), dan pengelolaan manajemen state yang berlebihan.

### 1.2 Visi Produk

**PyReact** adalah bahasa pemrograman fullstack terpadu (*Unified Fullstack Language*) berbasis Python. PyReact memungkinkan developer membangun aplikasi AI, Dashboard, SaaS, dan Data Science berkinerja tinggi hanya dengan menulis satu file tunggal `.pyreact`. Compiler PyReact secara otomatis mentranspilasikan dan memisahkan kode tersebut menjadi backend Flask (Python) dan frontend React/Tailwind (JavaScript).

### 1.3 Filosofi Zero-Cost & Open Source

Komitmen utama PyReact adalah **100% Gratis dan Bebas Biaya Operasional (Zero-Cost)** bagi developer:

1. **Lisensi Terbuka Permisif** — Dependensi berlisensi MIT, BSD, atau Apache 2.0 (Flask, React, Vite, Tailwind CSS, SQLAlchemy). Tidak ada library komersial berbayar.
2. **Database Tanpa Biaya Hosting** — Default menggunakan **SQLite** yang serverless, disimpan lokal, 100% gratis.
3. **Deployment Mandiri & Fleksibel** — Dockerfile dan konfigurasi Nginx bersifat cloud-agnostic. Bisa di-deploy gratis di Render, Fly.io, Oracle Cloud Free Tier, atau VPS mandiri.
4. **Tooling & IDE Extension Gratis** — VS Code extension dan DevTools didistribusikan gratis tanpa fitur premium berbayar.

---

## 2. Core Architecture (Arsitektur Utama)

PyReact bekerja dengan memilah satu file sumber menjadi beberapa bagian utama menggunakan Lexer dan Parser terintegrasi:

```
app.pyreact
     │
     ▼
  Lexer  ──►  Parser  ──►  AST  ──►  CodeGenerator
  (lexer.py)  (parser.py)            │
                                     ├── dist/backend/   (Flask/FastAPI)
                                     ├── dist/frontend/  (React + Router)
                                     └── dist/manifest.json
```

### 2.1 Blok Bahasa PyReact

Satu file `.pyreact` terbagi menjadi beberapa blok deklaratif:

| Blok | Deskripsi |
|---|---|
| `server { }` | Logika backend Python. Semua fungsi terekspos otomatis sebagai API RPC via PyBridge™ |
| `component Name():` | Logika UI React dengan `use_state`, handler, dan JSX return |
| `style { }` | Token desain global (`primary`, `font`, `radius`, `background`) |
| `model Name { }` | Deklarasi model AI/ML (PyTorch, ONNX) yang di-load otomatis |
| `database { }` | Konfigurasi koneksi database & ORM (SQLAlchemy) |
| `dependencies { }` | Deklarasi modul eksternal (`pip` / `npm`) |
| `shared_state { }` | State global yang disinkronkan lintas komponen |
| `pages { }` | Routing eksplisit dengan guard & layout support *(Fase 16)* |
| `agent Name { }` | Agen AI LLM terstruktur terhubung ke `UI.Chatbot` |
| `pipeline Name { }` | Pipeline AI multi-step (chain of agents) |

### 2.2 Modul Compiler

| File | Deskripsi |
|---|---|
| `compiler/lexer.py` | Tokenizer dual-syntax (brace `{}` + Python indent) |
| `compiler/parser.py` | AST builder — 11 node type |
| `compiler/codegen.py` | Multi-target code generator (~3.500 baris) |
| `compiler/router.py` | File-system routing & pages block generator *(Fase 16)* |
| `compiler/healer.py` | Self-Healing Compiler via Ollama *(Fase 15)* |
| `compiler/ai.py` | AI code generation (Ollama + rule-based fallback) |
| `compiler/audit.py` | Security audit engine (SQL Injection, XSS, CORS) |
| `compiler/lsp.py` | Language Server Protocol (autocompletion IDE) |
| `compiler/ppr.py` | PyReact Package Registry |

---

## 3. Spesifikasi Fungsional & Status Implementasi

### 3.1 Transpiler & Compiler Pipeline

- **R-3.1.1 (Parser Dual-Syntax):** Mendukung gaya deklarasi blok berbasis `{}` maupun indentasi Python. **[SELESAI]**
- **R-3.1.2 (JS Handler Transpiler):** Menerjemahkan ekspresi logika handler komponen (`if/else`, `for`, penugasan variabel) dari Python ke JavaScript murni menggunakan AST via modul `ast` Python. **[SELESAI]**
- **R-3.1.3 (Tipe Primitif):** Mengonversi otomatis `None/True/False` → `null/true/false`. **[SELESAI]**
- **R-3.1.4 (Indentasi):** Penyelarasan `textwrap.dedent` sebelum parsing AST. **[SELESAI]**

### 3.2 PyBridge™ RPC

- **R-3.2.1 (Zero-Boilerplate):** Panggil fungsi backend langsung via `server.nama_fungsi()` tanpa `fetch()` manual. **[SELESAI]**
- **R-3.2.2 (File Upload):** Mendukung pengiriman file biner via `FormData` dari `UI.Upload`. **[SELESAI]**
- **R-3.2.3 (Flask Context):** Memetakan parameter `form` dan `files` ke parameter fungsi Python secara otomatis. **[SELESAI]**

### 3.3 Dynamic Styling & Design Tokens

- **R-3.3.1 (CSS Variable Injection):** Token blok `style` disuntikkan ke `:root` CSS di `index.css`. **[SELESAI]**
- **R-3.3.2 (UI Theme Binding):** Semua komponen `UI.*` menggunakan variabel CSS tersebut secara dinamis. **[SELESAI]**

### 3.4 Developer Experience (DX)

- **R-3.4.1 (Live-Reload):** `pyreact dev` mendeteksi perubahan file `.pyreact` dan memicu kompilasi ulang → Vite HMR. **[SELESAI]**
- **R-3.4.2 (Cross-Platform):** Perintah `serve` dan `dev` berjalan di Windows (Waitress) dan Unix (Gunicorn). **[SELESAI]**

### 3.5 Self-Healing Compiler *(Fase 15)*

- **R-3.5.1 (Ollama Integration):** Flag `--heal` memanggil Ollama lokal (`localhost:11434`) saat terjadi `LexerError` atau `ParseError`. **[SELESAI]**
- **R-3.5.2 (Multi-Model):** Auto-detect model terbaik yang tersedia (codellama → qwen2.5-coder → gemma4 → llama3). **[SELESAI]**
- **R-3.5.3 (Iterative Retry):** Percobaan healing hingga 3x iterasi jika hasil masih mengandung error. **[SELESAI]**
- **R-3.5.4 (Diff & Backup):** Tampilkan diff perubahan, buat backup otomatis ke `.pyreact_heal_backups/`. **[SELESAI]**
- **R-3.5.5 (Fallback):** Rule-based healer berbasis regex saat Ollama offline. **[SELESAI]**

### 3.6 File-System Routing *(Fase 16)*

- **R-3.6.1 (Pages Block):** Sintaks `pages { Comp = "/path" [guard] }` untuk routing eksplisit. **[SELESAI]**
- **R-3.6.2 (FS Routing):** Scan otomatis folder `pages/` dengan konvensi Next.js (`[id].pyreact` → `/path/:id`). **[SELESAI]**
- **R-3.6.3 (react-router-dom v6):** Generate `BrowserRouter`, `Routes`, `Route`, `Navigate`, `useNavigate`. **[SELESAI]**
- **R-3.6.4 (Route Guard):** Komponen `RequireAuth` otomatis redirect ke `/login` jika tidak ada token. **[SELESAI]**
- **R-3.6.5 (Lazy Loading):** Semua page di-lazy-import via `React.lazy()` dengan `Suspense` fallback. **[SELESAI]**
- **R-3.6.6 (Router Manifest):** Generate file `_routes.txt` sebagai dokumentasi route yang dikompilasi. **[SELESAI]**

### 3.7 Type System & Validasi (Fungsi Total Flask & FastAPI) *(Fase 17)*

- **R-3.7.1 (Anotasi Tipe):** Mendukung anotasi tipe data parameter (`String`, `Number`, `Boolean`, `Optional[T]`) dan tipe kembalian fungsi di dalam blok `server`. **[SELESAI]**
- **R-3.7.2 (Pydantic Schema Generation):** Menghasilkan skema validasi Pydantic (`Schema_<fungsi>`) secara otomatis di backend Flask dan FastAPI. **[SELESAI]**
- **R-3.7.3 (Validasi Parameter Runtime):** Melakukan validasi payload JSON dan form data menggunakan skema Pydantic sebelum memanggil fungsi backend. **[SELESAI]**
- **R-3.7.4 (Penanganan ValidationError):** Menangkap `ValidationError` Pydantic dan mengembalikan response JSON error dengan status HTTP 400. **[SELESAI]**
- **R-3.7.5 (TypeScript Type Generation):** Menghasilkan berkas tipe deklarasi TypeScript `pybridge.d.ts` secara otomatis di frontend yang mendefinisikan interface `ServerBridge` lengkap dengan parameter opsional dan tipe data yang sesuai. **[SELESAI]**

### 3.8 Real-Time & WebSocket Lanjut *(Fase 18)*

- **R-3.8.1 (Blok Realtime):** Mendukung parsing blok `realtime { }` untuk menentukan provider real-time dan saluran (channels). **[SELESAI]**
- **R-3.8.2 (Autentikasi Token):** Mendukung ekstraksi dan autentikasi token JWT pada koneksi real-time (query parameter token pada WS dan args pada SSE). **[SELESAI]**
- **R-3.8.3 (Dukungan WebSocket):** Menyediakan endpoint WebSocket `/api/ws` berkinerja tinggi untuk backend FastAPI dengan integrasi event callback (`on_connect`, `on_message`, `on_disconnect`). **[SELESAI]**
- **R-3.8.4 (Dukungan Server-Sent Events / SSE):** Menyediakan stream data real-time `/api/sse` dan endpoint pengiriman `/api/realtime/send` untuk backend Flask sebagai fallback zero-dependency. **[SELESAI]**
- **R-3.8.5 (Broadcast API):** Menyediakan utilitas broadcast otomatis `broadcast(topic, data)` ke seluruh client terhubung baik di runtime Flask maupun FastAPI. **[SELESAI]**
- **R-3.8.6 (Presence & Event Callback):** Meneruskan identitas user hasil dekode JWT (atau ID acak) ke callback real-time untuk penanganan status online/presence secara custom. **[SELESAI]**

---

## 4. Rencana Rilis & Peta Jalan

### Fase 1: Dasar Compiler & CLI ✅ Selesai
- [x] Parser & Lexer untuk blok `server`, `component`, `style`, `model`
- [x] CLI dengan perintah `new`, `dev`, `serve`
- [x] File watcher (auto-recompile saat `.pyreact` disimpan)
- [x] Kompatibilitas Windows (Waitress fallback)

### Fase 2: Transpiler AST & Fungsionalitas Inti ✅ Selesai
- [x] Transpiler Python→JS berbasis AST (`if/elif/else`, array, dict, literal)
- [x] Normalisasi whitespace indentasi di compiler
- [x] Multipart payload untuk file upload di backend Flask

### Fase 3: AI-Native Integrations & Deployment ✅ Selesai
- [x] Auto-binding model loaders ke context fungsi `server`
- [x] Visualisasi chart interaktif SVG (`UI.Chart`) tanpa npm dependency
- [x] Template deployment: Dockerfile multi-stage, Nginx reverse proxy, `fly.toml`

### Fase 4: Production Readiness & Database ✅ Selesai
- [x] Source mapping & diagnostics (Elm-style caret error highlighting)
- [x] Blok `dependencies` (pip & npm) terintegrasi langsung di `.pyreact`
- [x] Blok `database` + SQLAlchemy ORM auto-setup
- [x] JWT built-in auth: `/api/login`, `/api/me`, `UI.useAuth()`, token interceptor di `pybridge.js`

### Fase 5: Optimasi Performa & State Management ✅ Selesai
- [x] Incremental re-compilation (skip write jika konten identik → hemat HMR reload)
- [x] Blok `shared_state` → `store.js` Pub/Sub tanpa library tambahan
- [x] Automatic code splitting via `React.lazy` + `<React.Suspense>`

### Fase 6: IDE Integration & Developer Tooling ✅ Selesai
- [x] VS Code Extension (`.pyreact` file association, TextMate grammar)
- [x] LSP (Language Server Protocol) — JSON-RPC, autocompletion `server.*`, `UI.*`, `shared.*`
- [x] PyReact DevTools — overlay HUD glassmorphic, RPC call log, shared state monitor

### Fase 7: Enterprise Scaling & Serverless ✅ Selesai
- [x] Multi-target backend: `--target flask` / `--target fastapi` / `--target serverless` (Mangum + AWS Lambda)
- [x] Static Site Generation (SSG) — pre-render ke `dist/static/index.html` (Tailwind CDN + Google Fonts)
- [x] Security Audit Engine (`--audit`) — deteksi SQL Injection, XSS, CORS wildcard

### Fase 8: AI-Assisted Development ✅ Selesai
- [x] PyReact Copilot (`pyreact ai "<prompt>"`) — generate file `.pyreact` lengkap secara instan
- [x] Natural Language block (`#ai "..."`) — pre-processing komentar menjadi kode valid di AST pipeline
- [x] 100% Offline-First: Ollama (`localhost:11434`) + rule-based fallback template generator

### Fase 9: Real-time Collaborative Engine ✅ Selesai
- [x] PyReact Studio (`/studio`) — visual editor drag-and-drop, dua arah visual-to-code sync via `/api/studio/save`
- [x] Real-time state sync WebSockets (`/api/ws`) + hook `useSyncState()` di `pybridge.js`

### Fase 10: Multi-Platform & Native Compilation ✅ Selesai
- [x] Desktop target (`--target desktop`) — `dist/desktop/src-tauri/` (Electron/Tauri, `.exe`, `.dmg`, `.app`)
- [x] Mobile target (`--target mobile`) — `dist/mobile/` Expo/React Native (mapping `UI.*` → native components)

### Fase 11: Global Ecosystem & Community Hub ✅ Selesai
- [x] PyReact Package Registry (PPR) — `pyreact install`, `pyreact publish`, `pyreact ppr`
- [x] Hub Marketplace — `pyreact new <name> --template <nama>` (template: `saas`, `ai-dashboard`, `landing-page`)

### Fase 12: Agen AI Lanjut & Pengujian Terpadu ✅ Selesai
- [x] Blok `agent` & `pipeline` — route `/api/agent/<name>`, `/api/pipeline/<name>`, Ollama + fallback heuristic
- [x] Unified Testing Framework — `pyreact test` (pytest + vitest berjalan simultan)
- [x] Perluasan UI Library — `UI.Modal`, `UI.Tabs`, `UI.Dropdown`, `UI.Accordion`, `UI.Calendar`, `UI.Chatbot`

### Fase 13: WebAssembly & Edge Compilation ✅ Selesai
- [x] WASM target (`--target wasm`) — backend Python berjalan 100% di browser via Pyodide
- [x] Edge target (`--target edge`) — transpilasi ke Cloudflare Workers / Vercel Edge Runtime (`worker.js`, `wrangler.toml`)

### Fase 14: Migrasi Database Otomatis & Panel Admin ✅ Selesai
- [x] Automated migrations — deteksi perubahan skema model, `ALTER TABLE` otomatis tanpa hapus data
- [x] Glassmorphic Admin Console (`/admin`) — CRUD database visual premium bawaan

### Fase 15: Self-Healing Compiler & AI Auto-Healing ✅ Selesai

**File baru:** `pyreact/compiler/healer.py`

- [x] Flag `--heal` pada `pyreact compile` dan `pyreact dev`
- [x] Auto-detect & pilih model Ollama terbaik yang tersedia secara otomatis
- [x] Flag `--model <nama>` untuk memilih model secara manual
- [x] Iterative retry hingga 3x percobaan jika kode hasil healing masih error
- [x] Diff viewer — tampilkan perubahan baris sebelum & sesudah healing
- [x] Backup otomatis ke folder `.pyreact_heal_backups/` sebelum file ditimpa
- [x] Rule-based fallback healer berbasis regex untuk error umum saat Ollama offline
- [x] Windows-safe output (cp1252 encoding-proof)
- [x] Flag `--no-diff` dan `--no-backup`

**Contoh output:**
```
+==================================================+
|    PyReact Self-Healing Compiler  [Fase 15]     |
+==================================================+

[ERROR] Kompilasi gagal: Expected IDENTIFIER, got LBRACE '{'
[ERROR] Lokasi: Baris 4, Kolom 11
[HEAL]  Model terpilih: gemma4:31b-cloud
[HEAL]  Mengirim ke Ollama (Percobaan 1/3)...
[HEAL]  Self-Healing BERHASIL pada percobaan ke-1!

[HEAL]  Perubahan yang dilakukan oleh AI:
  - component {
  + component MyComponent():
```

### Fase 16: File-System Routing & Nested Page Blocks ✅ Selesai

**File baru:** `pyreact/compiler/router.py`

- [x] Blok `pages { }` — routing eksplisit dengan opsi `[guard]` dan `[layout=NamaKomponen]`
- [x] File-system routing — scan otomatis folder `pages/` dengan konvensi Next.js
- [x] Dynamic segments — `[id].pyreact` dikompilasi menjadi `/path/:id`
- [x] File khusus `404.pyreact` → komponen Not Found route `*`
- [x] File khusus `_layout.pyreact` → layout wrapper (tidak dijadikan route)
- [x] Generate `BrowserRouter`, `Routes`, `Route`, `Navigate` dari react-router-dom v6
- [x] `RequireAuth` — route guard otomatis redirect ke `/login` jika token tidak ada
- [x] Lazy loading semua page via `React.lazy()` dengan `PageLoader` spinner animasi
- [x] Global `navigate()` helper — bisa dipanggil dari luar komponen React
- [x] Router Manifest `_routes.txt` — dokumentasi route hasil kompilasi
- [x] Auto-inject `react-router-dom: ^6.22.0` ke `package.json`

**Sintaks pages block:**
```pyreact
pages {
    Home      = "/"
    About     = "/about"
    Dashboard = "/dashboard" [guard]
    Settings  = "/settings"  [guard, layout=AppLayout]
    Profile   = "/profile/:id"
    Login     = "/login"
}
```

**File-system routing (folder `pages/`):**
```
pages/
  index.pyreact          →  /
  about.pyreact          →  /about
  blog/index.pyreact     →  /blog
  blog/[slug].pyreact    →  /blog/:slug
  user/[id].pyreact      →  /user/:id
  404.pyreact            →  * (Not Found)
  _layout.pyreact        →  Layout wrapper
```

### Fase 17: Type System & Validasi ✅ Selesai

**Modifikasi pada file:** `pyreact/compiler/parser.py`, `pyreact/compiler/codegen.py`

- [x] Parsing otomatis anotasi tipe data parameter (`String`, `Number`, `Boolean`, `Optional[T]`) pada fungsi di dalam blok `server`.
- [x] Auto-generation skema Pydantic (`Schema_<fungsi>`) di Flask backend (`_gen_routes`) dan FastAPI backend (`_gen_backend_fastapi`).
- [x] Penanganan runtime validation error secara otomatis dengan mengembalikan response status HTTP 400 berisi detail error terstruktur.
- [x] Auto-generation berkas deklarasi tipe TypeScript `pybridge.d.ts` di frontend (`_gen_frontend`) untuk mendukung autocompletion dan type-safe client-side calls.
- [x] Penulisan unit test (`test_fase15.py`) untuk memverifikasi fungsionalitas parsing, validasi, dan generasi kode.

### Fase 18: Real-Time & WebSocket Lanjut ✅ Selesai

**Modifikasi pada file:** `pyreact/compiler/lexer.py`, `pyreact/compiler/parser.py`, `pyreact/compiler/codegen.py`

- [x] Blok `realtime { }` untuk WebSocket channels dan konfigurasi.
- [x] Server-sent events (SSE) support pada backend Flask (`/api/sse` dan `/api/realtime/send`) dengan dynamic broadcast queue.
- [x] WebSockets support pada backend FastAPI (`/api/ws`) dengan client tracking dan authentication token.
- [x] Live data binding & synchronization helper `useSyncState` di frontend `pybridge.js` dengan fallback otomatis ke SSE jika WebSocket gagal.
- [x] Presence awareness dengan meneruskan identitas client ke callback `on_connect`, `on_message`, dan `on_disconnect`.
- [x] Test suite komprehensif (`test_fase18.py`) yang memvalidasi lexer, parser, codegen, dan custom handlers.

### Fase 19: Testing Framework Terpadu ✅ Selesai

**Modifikasi pada file:** `pyreact/compiler/tester.py`, `pyreact/compiler/codegen.py`, `pyreact/cli.py`

- [x] Generator unit test otomatis untuk endpoint backend (`test_backend_generated.py`) berdasarkan definisi tipe parameter pada blok `server`.
- [x] Mesin snapshot testing komponen frontend dengan zero-dependency static renderer (`render_jsx_to_mock_html`) membandingkan render output JSX dengan snapshot baseline.
- [x] Generator skrip E2E Playwright (`test_e2e_generated.py`) terintegrasi.
- [x] Integrasi generator coverage report HTML (`coverage`) ke console hasil eksekusi pengujian.
- [x] CLI command `pyreact test` untuk meluncurkan seluruh rangkaian test unit, E2E, dan snapshot secara bersamaan.

### Fase 20: VS Code Extension Penuh ✅ Selesai

**Modifikasi pada file:** `vscode-extension/package.json`, `vscode-extension/syntaxes/pyreact.tmLanguage.json`, `vscode-extension/src/extension.js`, `pyreact/compiler/lsp.py`

- [x] Hybrid syntax highlighting (.pyreact) yang menggabungkan tokenizing Python (pada blok `server` & `realtime`) dan JavaScript/JSX (pada blok `component`).
- [x] IntelliSense, trigger character autocomplete untuk RPC backend (`server.`), UI components (`UI.`), shared states (`shared.`), db helpers (`db.`), dan React Hooks.
- [x] Diagnostik inline secara real-time yang mem-parsing dokumen saat terbuka/diubah serta memberikan warning format penulisan komponen.
- [x] Fitur Quick-Fix code actions (seperti otomatis mengkapitalisasi penulisan nama komponen).
- [x] Cross-boundary jump-to-definition (dari pemanggilan `server.<fungsi>` di JSX langsung menuju deklarasi `def <fungsi>` di blok Python server).
- [x] Live Preview panel terintegrasi di VS Code yang menampilkan aplikasi berjalan secara aktual.

### Fase 21: PyReact Cloud ✅ Selesai

**Modifikasi pada file:** `pyreact/cli.py`

- [x] Perintah `pyreact deploy` untuk mengompres, membundel build `dist`, dan mengunggah bundel ke endpoint deployment cloud (`deployment.zip`).
- [x] Manajemen variabel secrets (`pyreact secrets set/list/remove`) yang disimpan di `.pyreact_secrets.json` dan dilekatkan pada deployment.
- [x] Manajemen custom domain mapping (`pyreact domain add/list/remove`) dengan integrasi record CNAME SSL.
- [x] Replika dashboard pemantauan cloud lokal interaktif (`dist/dashboard.html`) dengan visualisasi grafik live requests/second dan latency memanfaatkan Chart.js.

### Fase 22: Server-Side Rendering (SSR) Hybrid ✅ Selesai

**Modifikasi pada file:** `pyreact/compiler/codegen.py`, `routes.py`, `ssr.py`

- [x] Transpiler JSX AST ke f-string template Python (`ssr.py`) yang melakukan pemetaan UI elements serta penanganan nested components secara dinamis.
- [x] Zero-dependency server-side rendering pada backend Python (Flask & FastAPI) tanpa memerlukan process runtime Node.js eksternal.
- [x] Integrasi dynamic SSR engine ke entry route (`/`) di Flask & FastAPI untuk pre-rendering awal yang optimal bagi search engine crawler (SEO).
- [x] Mekanisme client-side hydration otomatis pada React root entry (`main.jsx`) yang mendeteksi konten SSR serta mengaktifkan `ReactDOM.hydrateRoot`.

### Fase 23: Offline-First PWA & Background Sync ✅ Selesai

**Modifikasi pada file:** `pyreact/compiler/codegen.py`, `sw.js`, `manifest.json`

- [x] Auto-generasi berkas `sw.js` (Service Worker) dan `manifest.json` untuk membuat web application bersifat installable.
- [x] Implementasi Offline RPC Queue untuk antrean transaksi/panggilan `server.*` saat perangkat sedang offline.
- [x] Integrasi IndexedDB/LocalStorage untuk cache state komponen secara otomatis.
- [x] Penyusunan komponen bawaan `UI.NetworkStatus` untuk menampilkan status koneksi secara real-time.

---

## 5. CLI Commands Lengkap

```bash
# Project
pyreact new <name>
pyreact new <name> --template <nama>       # saas | ai-dashboard | landing-page

# Development
pyreact dev                                # Flask + Vite dev servers
pyreact dev --heal                         # + AI self-healing aktif

# Compile
pyreact compile [file]                     # Default: app.pyreact → dist/
pyreact compile [file] --out <dir>         # Custom output directory
pyreact compile [file] --target flask      # Default target
pyreact compile [file] --target fastapi
pyreact compile [file] --target serverless
pyreact compile [file] --target wasm
pyreact compile [file] --target edge
pyreact compile [file] --target desktop
pyreact compile [file] --target mobile
pyreact compile [file] --audit             # + Security audit
pyreact compile [file] --ssg               # + Static Site Generation
pyreact compile [file] --heal              # + AI auto-heal error
pyreact compile [file] --heal --model codellama
pyreact compile [file] --heal --no-diff
pyreact compile [file] --heal --no-backup

# Production
pyreact build
pyreact serve

# AI
pyreact ai "<prompt>"

# Scaffold
pyreact generate component <Name>

# Package Registry
pyreact install <package>
pyreact publish <file>
pyreact ppr
pyreact hub

# Testing
pyreact test
```

---

## 6. Struktur Output Compiler

```
dist/
├── backend/
│   ├── app.py                Flask/FastAPI application
│   ├── routes.py             Auto-generated API endpoints
│   ├── generated_api.py      Kode dari blok server {}
│   ├── models.py             SQLAlchemy ORM models
│   └── requirements.txt      Python dependencies
└── frontend/
    ├── index.html
    ├── package.json          Termasuk react-router-dom (jika ada pages)
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── App.jsx           BrowserRouter + Routes (Fase 16)
        ├── main.jsx
        ├── index.css         Tailwind + CSS variables dari style {}
        ├── pybridge.js       PyBridge™ RPC client
        ├── pybridge.d.ts     TypeScript declaration file (Fase 17)
        ├── store.js          Shared state Pub/Sub
        ├── _routes.txt       Router manifest (Fase 16)
        ├── <Component>.jsx   Satu file per komponen
        └── ui/
            ├── components.jsx  UI Component Library (30+)
            ├── Admin.jsx       Admin Console (jika ada database)
            ├── Studio.jsx      Visual Editor
            └── DevTools.jsx    DevTools HUD
```

---

## 7. UI Component Library (30+)

```
Layout:      UI.Page, UI.Navbar, UI.Sidebar, UI.Dashboard
Forms:       UI.Input, UI.TextArea, UI.Select, UI.Upload
Data:        UI.Card, UI.Table, UI.DataGrid, UI.MetricCard
Charts:      UI.Chart (bar | line | pie)
Feedback:    UI.Alert, UI.Toast, UI.Spinner, UI.Badge
Navigation:  UI.Tabs, UI.Dropdown, UI.Accordion
Media:       UI.Calendar, UI.Modal
AI:          UI.Chatbot
Rich Text:   UI.Heading, UI.Text, UI.Divider
Routing:     UI.Link, UI.NavLink              ← Fase 16
Auth:        UI.useAuth()
```

---

## 8. Kriteria Penerimaan (Acceptance Criteria)

1. **Keberhasilan Kompilasi** — File `.pyreact` yang valid menghasilkan folder `dist/` tanpa error sintaksis baik di Python maupun JavaScript.
2. **Kesesuaian Desain** — Perubahan warna di blok `style` mengubah warna komponen UI di browser secara instan.
3. **Kepatuhan Lintas Platform** — `pyreact serve` dan `pyreact dev` berjalan di Windows (Powershell) dan macOS/Linux terminal tanpa crash encoding.
4. **Self-Healing Terukur** — `--heal` berhasil memperbaiki minimal 80% syntax error sederhana (missing colon, salah nama blok) dalam 1 percobaan.
5. **Routing Konsisten** — Semua route di blok `pages { }` menghasilkan `<Route>` yang sesuai di `App.jsx`, dan route ber-`[guard]` dibungkus `RequireAuth`.

---

## 9. Riwayat Pengembangan / Log Histori

**5 Juni 2026 — Fase 17: Type System & Validasi:**
- Upgrade parser AST (`parser.py`) untuk mendukung anotasi tipe data parameter dan return type fungsi di blok `server`.
- Implementasi auto-generation skema Pydantic (`Schema_<fungsi>`) di backend Flask (`_gen_routes`) dan FastAPI (`_gen_backend_fastapi`).
- Penambahan penanganan error `ValidationError` (status code 400) pada API routes.
- Implementasi auto-generation file tipe deklarasi TypeScript `pybridge.d.ts` di frontend (`_gen_frontend`) untuk mendukung autocompletion dan type-safe client-side calls.
- Penulisan test suite lengkap (`test_fase15.py`) dan penyelesaian pengujian dengan sukses 100%.

**4 Juni 2026 — Fase 16: File-System Routing & Nested Page Blocks:**
- Implementasi modul `pyreact/compiler/router.py` — `RouterCodeGenerator`, `parse_pages_block()`, `scan_pages_folder()`.
- Upgrade `_parse_pages()` di `parser.py` — menyimpan raw meta string lengkap termasuk `[guard]`, `[layout=X]`.
- Upgrade `_gen_frontend()` di `codegen.py` — auto-inject `react-router-dom` ke `package.json` jika ada routing config.
- Upgrade `_gen_app_jsx()` di `codegen.py` — delegasi ke `RouterCodeGenerator` jika ada `RouterConfig`, fallback ke single-page mode jika tidak ada.
- Generate router manifest `_routes.txt` di setiap kompilasi yang menggunakan routing.

**4 Juni 2026 — Fase 15: Self-Healing Compiler:**
- Implementasi modul `pyreact/compiler/healer.py` (kelas `SelfHealingCompiler`, `RuleBasedHealer`).
- Integrasi flag `--heal` ke CLI `compile` dan `dev` dengan multi-model auto-detection.
- Upgrade `_compile()` di `cli.py` untuk delegasikan healing ke modul terpisah.
- Perbaikan encoding Windows (cp1252) pada `_safe_print()` dan penggantian Unicode box chars ke ASCII.
- Perbaikan `_get_available_models()` untuk menggunakan nama model lengkap (dengan tag, misal `gemma4:31b-cloud`) agar API request tidak 404.

**4 Juni 2026 — Penyelesaian Fase 1–14 (MVP):**
- Compiler pipeline: Lexer + Parser + AST + CodeGenerator.
- PyBridge™ RPC (JSON + multipart), UI Library (30+), Dynamic Theming.
- Database ORM + Auto-Migration, JWT Auth bawaan.
- Shared State (Pub/Sub store.js), Live-Reload Watcher.
- AI Agents & Pipelines, Security Audit Engine.
- Deployment multi-target (Flask / FastAPI / Serverless / WASM / Edge / Desktop / Mobile).
- PPR Registry + Hub Marketplace Templates.
- PyReact Studio (visual editor), DevTools HUD.
- VS Code Extension + LSP autocompletion.

---

## 10. Roadmap: Fase Selanjutnya

### Fase 17: Type System & Validasi ✅ Completed (5 Juni 2026)
- Anotasi tipe PyReact: `String`, `Number`, `Boolean`, `List[T]`, `Dict[K,V]`
- Runtime validation otomatis di backend via Pydantic
- TypeScript type generation untuk frontend
- Penyiapan metadata tipe untuk IDE autocomplete berbasis type via LSP

### Fase 18: Real-Time & WebSocket Lanjut ✅ Completed (5 Juni 2026)
- [x] Blok `realtime { }` untuk WebSocket channels
- [x] Server-sent events (SSE) support
- [x] Live data binding ke komponen UI
- [x] Presence awareness (siapa yang sedang online)

### Fase 19: Testing Framework Terpadu ✅ Completed (5 Juni 2026)
- [x] Unit test generator otomatis dari blok `server { }`
- [x] Component snapshot testing
- [x] End-to-end test runner (Playwright integration)
- [x] Coverage report HTML

### Fase 20: VS Code Extension Penuh ✅ Completed (5 Juni 2026)
- [x] Syntax highlighting `.pyreact` yang sempurna
- [x] IntelliSense & autocomplete berbasis LSP
- [x] Inline compiler error dengan quick-fix suggestion
- [x] PyBridge jump-to-definition
- [x] Live preview panel terintegrasi

### Fase 21: PyReact Cloud ✅ Completed (5 Juni 2026)
- [x] `pyreact deploy` — one-command cloud deployment
- [x] Project dashboard di pyreact.cloud
- [x] Shared secrets management
- [x] Custom domain support
- [x] Analytics & monitoring built-in

### Fase 22: Server-Side Rendering (SSR) Hybrid ✅ Completed (5 Juni 2026)
- [x] Transpilasi AST JSX ke f-string template Python (`ssr.py`)
- [x] Zero-dependency rendering di backend Flask tanpa Node.js
- [x] Integrasi SSR ke entry route Flask (`routes.py`) untuk SEO optimal
- [x] Client-side hydration script di entry point React (`main.jsx`)

### Fase 23: Offline-First PWA & Background Sync ✅ Completed (5 Juni 2026)
- [x] Auto-generasi Service Worker (`sw.js`) dan Web App Manifest (`manifest.json`)
- [x] Implementasi Offline RPC Queue untuk menyimpan dan memutar kembali transaksi/call saat offline
- [x] Mekanisme local state caching otomatis memanfaatkan IndexedDB/LocalStorage
- [x] Penyediaan komponen UI indikator status koneksi bawaan (`UI.NetworkStatus`)

### Fase 24: Real-time Collaborative State & WebSockets 🔲 Planned
- [ ] Implementasi backend WebSocket handler di Flask/FastAPI (blok `realtime` support)
- [ ] Auto-synchronization `shared_state` lintas client menggunakan WebSocket broadcast
- [ ] Mekanisme deteksi konflik dan state merging (CRDT-lite) secara otomatis
- [ ] Penyediaan React hooks real-time (`useRealtimeChannel`)

### Fase 25: GraphQL API Engine & Type-Safe Queries 🔲 Planned
- [ ] Auto-generate schema GraphQL berdasarkan model database & ORM
- [ ] Penyediaan server endpoint `/graphql` bawaan pada target Flask & FastAPI
- [ ] Auto-generasi hook React klien (`useQuery` / `useMutation`) dengan filter/sorting deklaratif

### Fase 26: RBAC (Role-Based Access Control) & Route Guards 🔲 Planned
- [ ] Integrasi otentikasi JWT bawaan di backend dan enkripsi token di klien
- [ ] Decorator backend Python `@role_required` untuk proteksi endpoint RPC/API secara terperinci
- [ ] Peningkatan dynamic route guards di frontend untuk membatasi navigasi berbasis peran pengguna

---

*PyReact PRD v1.4.0 — Last updated: 5 Juni 2026*
*© Yuda Hasibuan — MIT License*
