# PyReact-Web 🚀

**Bahasa Web Fullstack Modern Bertenaga Python** — v1.4.0

> Bangun aplikasi fullstack bertenaga AI yang indah menggunakan satu bahasa, satu berkas, dan satu alur kerja terpadu.
>
> **PyReact = Kesederhanaan Python + Kekuatan React + Pengembangan AI-Native**

---

## 📌 Navigasi Cepat
* [📦 Instalasi & Memulai Cepat](#-instalasi--memulai-cepat)
* [🗺️ Mental Model untuk Developer](#-mental-model-untuk-developer)
* [📂 Konvensi Struktur Berkas](#-konvensi-struktur-berkas)
* [📄 Satu Berkas, Stack Utuh (Full Stack)](#-satu-berkas-stack-utuh-full-stack)
* [⚡ Fitur Utama](#-fitur-utama)
* [📚 Panduan & Referensi Penting](#-panduan--referensi-penting)

---

## 📦 Instalasi & Memulai Cepat

PyReact tersedia secara resmi di PyPI dengan nama package `pyreact-web`:

```bash
# 1. Instal PyReact secara global atau di venv
pip install pyreact-web

# 2. Buat proyek baru
pyreact new myapp

# 3. Masuk ke direktori proyek
cd myapp

# 4. Jalankan server pengembangan Flask (Backend) + Vite (Frontend)
pyreact dev
```

---

## 🗺️ Mental Model untuk Developer

PyReact dirancang agar familiar bagi Anda yang sudah terbiasa dengan ekosistem Flask (Python) dan React (JavaScript).

### 🐍 Dari Flask ke PyReact
* Tidak perlu mendefinisikan rute `@app.route` manual. Cukup tulis fungsi Python biasa di dalam blok `server { }`. Fungsi tersebut otomatis diekspos sebagai API aman.
* Pengiriman data menggunakan parameter fungsi biasa (dengan bantuan Pydantic).

### ⚛️ Dari React ke PyReact
* State dideklarasikan seperti React hook biasa tetapi dalam snake_case Python: `val, setVal = use_state(initial)`.
* Tidak ada proses impor React manual, semuanya ditangani otomatis oleh transpiler saat kompilasi.

---

## 📂 Konvensi Struktur Berkas

Setiap proyek PyReact menghasilkan struktur standar untuk memudahkan AI (seperti Cursor/Claude/Copilot) memahami kode Anda:

```
myapp/
├── app.pyreact          ← File entry point utama aplikasi Anda
├── AGENTS.md            ← Panduan bahasa PyReact khusus untuk asisten AI
├── COOKBOOK.md          ← Koleksi resep kode siap pakai
├── .cursorrules         ← Aturan pengerjaan otomatis untuk Cursor IDE
└── components/          ← Direktori untuk meletakkan komponen tambahan
```

---

## 📄 Satu Berkas, Stack Utuh (Full Stack)

Berikut adalah contoh aplikasi minimal `.pyreact` yang menggunakan database, API, navigasi halaman, dan komponen UI bawaan:

```python
# app.pyreact
# @pyreact app
# @name: Demo App
# @description: Contoh kesatuan frontend-backend dalam satu file

database {
    provider = "sqlite"
    url = "tasks.db"
}

server {
    class DbTask(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=False)

    def get_tasks():
        tasks = DbTask.query.all()
        return [{"id": t.id, "title": t.title} for t in tasks]
}

component Home():
    tasks, setTasks = use_state([])

    def load():
        res = server.get_tasks()
        setTasks(res)

    use_effect(def():
        load()
    , [])

    return (
        <UI.Page>
            <UI.Navbar title="PyReact App" />
            <div className="pt-24 max-w-xl mx-auto px-4">
                <UI.Card title="Tasks List">
                    {tasks.map(t => (
                        <UI.Text key={t.id} className="p-2 border-b border-slate-700">{t.title}</UI.Text>
                    ))}
                </UI.Card>
            </div>
        </UI.Page>
    )

style {
    primary = "#6366f1"
    radius  = "12px"
}
```

---

## ⚡ Fitur Utama

* **🩺 Self-Healing Compiler**: Jalankan dengan `pyreact dev --heal` untuk memicu pemulihan AI otomatis (via Ollama) jika terdapat kesalahan sintaksis.
* **🌐 Hybrid Server-Side Rendering (SSR)**: Pre-rendering halaman di backend Python untuk performa SEO terbaik tanpa Node.js server.
* **📴 Offline-First PWA**: Dukungan otomatis Service Worker (`sw.js`) dan Offline RPC Queue untuk menyimpan transaksi klien saat luring.
* **🔄 WebSocket & Real-time**: Sinkronisasi state instan antar user via blok `realtime { }`.

---

## 📚 Panduan & Referensi Penting

Kami menyediakan dokumentasi khusus di dalam proyek ini:
* **[AGENTS.md](file:///c:/Users/Administrator/Downloads/Project/1/AGENTS.md)**: Gunakan ini sebagai referensi sintaksis lengkap. **Sangat direkomendasikan untuk dibaca oleh asisten AI** Anda sebelum melakukan pengkodean.
* **[COOKBOOK.md](file:///c:/Users/Administrator/Downloads/Project/1/COOKBOOK.md)**: Berisi 5 resep pola pengerjaan umum (CRUD, Login Auth, File Upload, Chart Dashboard, Real-time Collab) yang dapat disalin langsung.

---

## 📄 Lisensi

MIT © Yuda Hasibuan
