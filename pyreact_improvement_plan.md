# 🚀 PyReact — Plan Peningkatan DX (Developer Experience)

> **Tujuan:** Membuat AI (Cursor, Claude, Copilot, dll.) langsung memahami struktur PyReact seperti mereka memahami Flask & React, sehingga user bisa produktif secepat mungkin.

---

## 🎯 Masalah Utama Saat Ini

Saat AI diminta membuat sesuatu dengan PyReact, ada 3 masalah kritis:

1. **AI tidak tahu konteks** — AI menulis JSX/Flask mentah, bukan `.pyreact`
2. **Tidak ada "scaffolding" standar** — User bingung mulai dari mana
3. **Tidak ada referensi siap pakai per use-case** — Beda dengan Flask (`app.py`) atau React (`App.jsx`) yang sudah ada konvensi universal

---

## 📋 Plan Lengkap (Prioritas Tinggi → Rendah)

---

### 🔴 PRIORITAS 1 — Struktur "App Minimal" yang Standar

**Masalah:** Flask punya `app.py`. React punya `App.jsx`. PyReact belum punya equivalent yang dikenal AI secara universal.

**Solusi: Definisikan "App Minimal" standar:**

```python
# Minimal PyReact app (setara hello world Flask/React)
server {
    def hello():
        return {"message": "Hello from PyReact!"}
}

component App():
    msg, setMsg = use_state("")

    def load():
        data = server.hello()
        setMsg(data.message)

    return (
        <UI.Page>
            <UI.Navbar title="My App" />
            <div className="pt-24 text-center">
                <UI.Button onClick={load}>Click Me</UI.Button>
                {msg and <UI.Alert type="success">{msg}</UI.Alert>}
            </div>
        </UI.Page>
    )

style {
    primary = "#6366f1"
    radius  = "12px"
}
```

**Action Items:**
- [x] Tambahkan file `app.pyreact` sebagai entry point default (seperti `app.py` di Flask)
- [x] Update `pyreact new <name>` agar generate file `app.pyreact`
- [x] Dokumentasikan konvensi: **1 file = 1 app**, file utama selalu `app.pyreact`

---

### 🔴 PRIORITAS 2 — Template Starter yang Kaya

**Masalah:** `pyreact new <name>` belum menghasilkan struktur yang cukup informatif untuk AI.

**Solusi: 5 template starter:**

| Template | Perintah | Setara Di |
|---|---|---|
| `blank` | `pyreact new myapp` | `create-react-app` default |
| `crud` | `pyreact new myapp --template crud` | Flask + SQLite tutorial |
| `dashboard` | `pyreact new myapp --template dashboard` | React Admin |
| `auth` | `pyreact new myapp --template auth` | Flask-Login boilerplate |
| `saas` | `pyreact new myapp --template saas` | SaaS starter kit |

**Setiap template harus menghasilkan:**
```
myapp/
├── app.pyreact          <- Entry point utama
├── README.md            <- Cara run + struktur penjelasan
├── .env.example         <- Variabel environment
├── AGENTS.md            <- Copy dari root (untuk AI context)
└── COOKBOOK.md          <- Resep siap pakai
```

**Action Items:**
- [/] Tambah template `blank`, `crud`, `dashboard`, `collab`, `graphql`, `rbac`, `webrtc` ke `pyreact new` (Sudah ada di CLI, disinkronisasikan)
- [x] Setiap template generate `README.md` otomatis berisi penjelasan struktur
- [x] Setiap template generate `AGENTS.md` lokal agar AI selalu punya konteks
- [x] Setiap template generate `COOKBOOK.md` lokal agar AI selalu punya resep siap pakai

---

### 🔴 PRIORITAS 3 — AGENTS.md Improvement (Konteks AI)

**Masalah:** AGENTS.md sudah bagus tapi belum ada "Quick Reference Card" mapping ke Flask/React.

**Solusi: Tambahkan 3 section baru ke AGENTS.md:**

#### A. Pola Mapping Flask → PyReact
*(Lihat detail di [AGENTS.md](file:///c:/Users/Administrator/Downloads/Project/1/AGENTS.md))*

#### B. Pola Mapping React → PyReact
*(Lihat detail di [AGENTS.md](file:///c:/Users/Administrator/Downloads/Project/1/AGENTS.md))*

#### C. Decision Tree untuk AI
*(Lihat detail di [AGENTS.md](file:///c:/Users/Administrator/Downloads/Project/1/AGENTS.md))*

**Action Items:**
- [x] Tambah section "Flask -> PyReact Mental Model" ke `AGENTS.md`
- [x] Tambah section "React -> PyReact Mental Model" ke `AGENTS.md`
- [x] Tambah section "Decision Tree" ke `AGENTS.md`
- [x] Tambah section "File Header Convention" ke `AGENTS.md`

---

### 🟡 PRIORITAS 4 — Cookbook / Recipe Patterns

**Masalah:** Developer (dan AI) butuh pola siap pakai untuk kasus nyata.

**Solusi: Buat file `COOKBOOK.md`:**
Berisi 5 resep lengkap (CRUD, Auth JWT, File Upload, Dashboard Chart, WebSocket Collaborative State).

**Action Items:**
- [x] Buat file `COOKBOOK.md` di root project
- [x] Isi minimal 5 recipe paling common
- [x] Reference `COOKBOOK.md` dari `AGENTS.md` dan `README.md`

---

### 🟡 PRIORITAS 5 — Error Messages yang Lebih Informatif

**Masalah:** Ketika AI generate kode salah (misal pakai `useState`), error tidak memberikan solusi.

**Sebelum (saat ini):**
```
ParseError: Unexpected token 'useState'
```

**Sesudah (dengan improvement):**
```
ParseError: Unexpected token 'useState' at line 5
  Hint: Di PyReact, gunakan use_state() bukan useState()
  Contoh: val, setVal = use_state(False)
  Lihat: AGENTS.md#hooks-reference
```

**Action Items:**
- [x] Update `compiler/parser.py` dengan error hints
- [x] Update `compiler/lexer.py` dengan error hints
- [x] Buat file `pyreact/compiler/errors.py` (mapping error -> hint)

---

### 🟡 PRIORITAS 6 — `pyreact explain` CLI Command

**Masalah:** User baru dan AI sering tidak tau apa yang sudah di-generate.

**Output yang diharapkan:**
```bash
$ pyreact explain app.pyreact

app.pyreact Analysis:
  [OK] server block    -> 3 endpoints: /api/hello, /api/create_user, /api/get_tasks
  [OK] component App   -> State: [tasks, newTitle], Calls: server.get_tasks()
  [OK] database block  -> SQLite, Models: [DbTask]
  [OK] pages block     -> Routes: / (Home), /about (About), /dashboard [GUARDED]
  [OK] style block     -> primary=#6366f1, font=Inter

API Endpoints Generated:
  POST /api/hello          -> def hello()
  POST /api/create_user    -> def create_user(name: str, email: str)
  POST /api/get_tasks      -> def get_tasks()

Output: dist/backend/ + dist/frontend/
```

**Action Items:**
- [x] Tambah `pyreact explain [file]` ke `cli.py`
- [x] Parse AST dan tampilkan summary yang mudah dibaca
- [x] Tampilkan daftar endpoint yang akan di-generate

---

### 🟡 PRIORITAS 7 — `.pyreact` File Header Convention

**Masalah:** Ketika AI membuka file `.pyreact`, tidak ada metadata yang menjelaskan konteks.

**Solusi: Standar file header:**
```python
# @pyreact app
# @name: Task Manager
# @description: CRUD app untuk manajemen task
# @version: 1.0.0
# @blocks: server, database, component, pages, style
```

**Action Items:**
- [x] Definisikan standar metadata header `# @pyreact` di `AGENTS.md`
- [x] Update template generator untuk include header di file yang di-generate
- [x] Update compiler untuk membaca dan display metadata header (opsional)

---

### 🟢 PRIORITAS 8 — Interactive `pyreact init` Wizard

**Masalah:** `pyreact new <name>` langsung generate tanpa bertanya kebutuhan user.

**Action Items:**
- [x] Tambah `pyreact init` sebagai alias improvement dari `pyreact new`
- [x] Implementasi wizard berbasis input terminal
- [x] Generate file sesuai pilihan wizard

---

### 🟢 PRIORITAS 9 — `pyreact generate` yang Lebih Lengkap

**Masalah:** `pyreact generate component <Name>` hanya scaffold component kosong.

**Action Items:**
- [x] Update `cli.py` untuk support sub-commands extended (`--crud`, `page`, `api`, `model`, `auth`)
- [x] Buat template generator untuk setiap sub-command
- [x] Update `AGENTS.md` dengan daftar perintah generate baru

---

### 🟢 PRIORITAS 10 — README Rewrite

**Masalah:** README saat ini lebih mirip spec document daripada "Getting Started" guide.

**Action Items:**
- [x] Rewrite `README.md` dengan format "Getting Started" yang user-friendly
- [x] Tambah section "Untuk yang kenal React" dan "Untuk yang kenal Flask"
- [x] Tambah link ke AGENTS.md dan COOKBOOK.md

---

## 📊 Summary Progress (Impact vs Effort)

| # | Item | Impact | Effort | Status |
|---|------|--------|--------|--------|
| 1 | Standar file `app.pyreact` | Tinggi | Rendah | ✅ Selesai |
| 2 | Template starter yang kaya | Tinggi | Sedang | ✅ Selesai |
| 3 | AGENTS.md: mapping Flask/React | Tinggi | Rendah | ✅ Selesai |
| 4 | Cookbook / Recipe Patterns | Sedang | Sedang | ✅ Selesai |
| 5 | Error messages + hints | Sedang | Sedang | ✅ Selesai |
| 6 | `pyreact explain` command | Sedang | Sedang | ✅ Selesai |
| 7 | File header convention | Sedang | Rendah | ✅ Selesai |
| 8 | `pyreact init` wizard | Rendah | Tinggi | ✅ Selesai |
| 9 | `pyreact generate` extended | Rendah | Sedang | ✅ Selesai |
| 10 | README rewrite | Sedang | Rendah | ✅ Selesai |
| 11 | `pyreact doctor --fix` (Bonus) | Tinggi | Rendah | ✅ Selesai |

---

## 🗓 Status Sprint

### Sprint 1 — Quick Wins (SELESAI)
1. **[Selesai]** Update `AGENTS.md` dengan section mapping Flask/React -> PyReact + Decision Tree
2. **[Selesai]** Standarkan entry point: `app.pyreact` di `pyreact new`
3. **[Selesai]** Tambah file header convention ke `AGENTS.md`
4. **[Selesai]** Rewrite `README.md` agar lebih accessible
5. **[Selesai]** Buat `COOKBOOK.md` berisi 5 resep utama (CRUD, Auth, Upload, Chart, Collab)
6. **[Selesai]** Tambahkan auto-generate missing context files ke `pyreact doctor --fix`

### Sprint 2 — Developer Tooling & CLI UX (SELESAI)
7. **[Selesai]** Perbaiki error messages dengan hints di `compiler/errors.py`
8. **[Selesai]** Tambah `pyreact explain` command ke `cli.py`
9. **[Selesai]** Extend `pyreact generate` commands

### Sprint 3 — Wizard & Rich Scaffolders (SELESAI)
10. **[Selesai]** Buat `pyreact init` wizard interaktif
11. **[Selesai]** Sinkronisasi template starter yang lebih kaya (`crud`, `auth`, `dashboard` dll.)

### Sprint 6 — Deployment, Database Migrations, & Environment Management (SELESAI)
12. **[Selesai]** Wizard deployment `pyreact deploy --platform <vercel|fly|railway|render|digitalocean>`
13. **[Selesai]** Pengelolaan env `.env.pyreact` + `pyreact env check` command untuk verifikasi environment
14. **[Selesai]** Tooling database migration CLI `pyreact db [migrate|status|rollback]`


