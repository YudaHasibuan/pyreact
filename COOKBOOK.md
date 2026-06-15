# 🍳 PyReact Cookbook

Koleksi pola kode siap pakai (Recipe Patterns) untuk membantu Anda dan AI Asisten Anda dalam menulis aplikasi menggunakan PyReact.

---

## 📖 Daftar Resep
1. [Resep 1: Aplikasi CRUD Sederhana](#resep-1-aplikasi-crud-sederhana)
2. [Resep 2: Autentikasi JWT & Halaman Terproteksi](#resep-2-autentikasi-jwt--halaman-terproteksi)
3. [Resep 3: Unggah File (File Upload)](#resep-3-unggah-file-file-upload)
4. [Resep 4: Dasbor dengan Visualisasi Grafik (Chart)](#resep-4-dasbor-dengan-visualisasi-grafik-chart)
5. [Resep 5: Kolaborasi Real-time (Chat / Editor)](#resep-5-kolaborasi-real-time-chat--editor)

---

## Resep 1: Aplikasi CRUD Sederhana
Menggunakan database SQLite bawaan untuk melakukan operasi Create, Read, Update, Delete.

```python
database {
    provider = "sqlite"
    url = "items.db"
}

server {
    class DbItem(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)

    def get_items():
        items = DbItem.query.all()
        return [{"id": i.id, "name": i.name} for i in items]

    def add_item(name: str):
        if not name:
            return {"status": "error", "message": "Nama wajib diisi"}
        item = DbItem(name=name)
        db.session.add(item)
        db.session.commit()
        return {"status": "success", "id": item.id}

    def delete_item(item_id: int):
        item = DbItem.query.get(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return {"status": "success"}
        return {"status": "error", "message": "Item tidak ditemukan"}
}

component Home():
    items, setItems = use_state([])
    newItem, setNewItem = use_state("")

    def loadItems():
        res = server.get_items()
        setItems(res)

    def handleAdd():
        if newItem == "":
            return
        res = server.add_item(newItem)
        if res.status == "success":
            setNewItem("")
            loadItems()

    def handleDelete(id):
        res = server.delete_item(id)
        if res.status == "success":
            loadItems()

    use_effect(def():
        loadItems()
    , [])

    return (
        <UI.Page>
            <UI.Navbar title="Katalog Item" />
            <div className="pt-24 max-w-xl mx-auto px-4">
                <UI.Card title="Tambah Item Baru">
                    <div className="flex gap-2">
                        <UI.Input value={newItem} onChange={setNewItem} placeholder="Nama item..." className="flex-1" />
                        <UI.Button onClick={handleAdd}>Tambah</UI.Button>
                    </div>
                </UI.Card>

                <div className="mt-6 space-y-3">
                    {items.map(item => (
                        <div key={item.id} className="flex justify-between items-center p-4 bg-slate-800 rounded-lg border border-slate-700">
                            <UI.Text>{item.name}</UI.Text>
                            <UI.Button onClick={() => handleDelete(item.id)} variant="danger">Hapus</UI.Button>
                        </div>
                    ))}
                </div>
            </div>
        </UI.Page>
    )

style {
    primary = "#3b82f6"
    radius = "12px"
}
```

---

## Resep 2: Autentikasi JWT & Halaman Terproteksi
Membatasi akses rute dengan `[guard]` dan otentikasi bawaan.

```python
pages {
    Home      = "/"
    Dashboard = "/dashboard" [guard]
    Login     = "/login"
}

component Home():
    return (
        <UI.Page>
            <UI.Navbar title="Situs Publik" />
            <div className="pt-24 text-center">
                <UI.Heading>Selamat Datang di Portal Publik</UI.Heading>
                <div className="mt-4">
                    <a href="/login" className="text-blue-500 underline">Masuk ke Dashboard</a>
                </div>
            </div>
        </UI.Page>
    )

component Login():
    username, setUsername = use_state("")
    password, setPassword = use_state("")
    error, setError = use_state("")

    auth = UI.useAuth()

    def handleLogin():
        success = auth.login(username, password)
        if success:
            window.location.pathname = "/dashboard"
        else:
            setError("Username atau password salah")

    return (
        <UI.Page>
            <div className="min-h-screen flex items-center justify-center p-4">
                <UI.Card title="Form Login" className="w-full max-w-sm">
                    {error and <UI.Alert type="error" className="mb-4">{error}</UI.Alert>}
                    <UI.Input label="Username" value={username} onChange={setUsername} />
                    <UI.Input label="Password" value={password} onChange={setPassword} type="password" />
                    <UI.Button onClick={handleLogin} className="mt-4 w-full">Login</UI.Button>
                </UI.Card>
            </div>
        </UI.Page>
    )

component Dashboard():
    auth = UI.useAuth()

    def handleLogout():
        auth.logout()
        window.location.pathname = "/login"

    return (
        <UI.Page>
            <UI.Navbar title="Dashboard Admin" />
            <div className="pt-24 max-w-xl mx-auto px-4 text-center">
                <UI.Heading>Halaman Rahasia Terproteksi</UI.Heading>
                <UI.Text className="mt-2 text-gray-400">Hanya bisa diakses jika Anda sudah masuk.</UI.Text>
                <UI.Button onClick={handleLogout} variant="secondary" className="mt-6">Logout</UI.Button>
            </div>
        </UI.Page>
    )

style {
    primary = "#10b981"
    radius = "10px"
}
```

---

## Resep 3: Unggah File (File Upload)
Mengirimkan berkas binar dari frontend ke backend Flask secara otomatis.

```python
server {
    import os

    def upload_photo(file):
        upload_dir = "./uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        filepath = os.path.join(upload_dir, file.filename)
        file.save(filepath)
        
        return {"status": "success", "url": f"/uploads/{file.filename}"}
}

component Home():
    status, setStatus = use_state("")
    loading, setLoading = use_state(False)

    def handleFile(fileObj):
        setLoading(True)
        res = server.upload_photo(fileObj)
        if res.status == "success":
            setStatus(f"Berhasil diunggah: {res.url}")
        else:
            setStatus("Gagal mengunggah file.")
        setLoading(False)

    return (
        <UI.Page>
            <UI.Navbar title="File Uploader" />
            <div className="pt-24 max-w-md mx-auto px-4">
                <UI.Card title="Unggah Foto Anda">
                    <UI.Upload label="Pilih file gambar" onFile={handleFile} accept="image/*" />
                    {loading and <UI.Spinner className="mt-4" />}
                    {status and <UI.Alert type="info" className="mt-4">{status}</UI.Alert>}
                </UI.Card>
            </div>
        </UI.Page>
    )

style {
    primary = "#8b5cf6"
    radius = "8px"
}
```

---

## Resep 4: Dasbor dengan Visualisasi Grafik (Chart)
Menampilkan metrik performa dengan Chart bawaan SVG.

```python
server {
    def get_revenue_data():
        return {
            "chart_data": [
                {"label": "Jan", "value": 400},
                {"label": "Feb", "value": 600},
                {"label": "Mar", "value": 800},
                {"label": "Apr", "value": 500},
                {"label": "May", "value": 1200}
            ],
            "metrics": {
                "total": "$3,500",
                "growth": "+15%"
            }
        }
}

component Home():
    data, setData = use_state(None)

    use_effect(def():
        res = server.get_revenue_data()
        setData(res)
    , [])

    return (
        <UI.Page>
            <UI.Navbar title="Analytics Dashboard" />
            <div className="pt-24 max-w-4xl mx-auto px-4 space-y-6">
                <UI.Heading>Revenue Overview</UI.Heading>
                
                {data and (
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <UI.MetricCard label="Total Revenue" value={data.metrics.total} trend="up" />
                        <UI.MetricCard label="Monthly Growth" value={data.metrics.growth} trend="up" />
                        <UI.MetricCard label="Status" value="Healthy" />
                    </div>
                )}

                {data and (
                    <UI.Card title="Revenue Trend (Year-to-date)">
                        <UI.Chart type="line" data={data.chart_data} height={300} />
                    </UI.Card>
                )}
            </div>
        </UI.Page>
    )

style {
    primary = "#ec4899"
    radius = "16px"
}
```

---

## Resep 5: Kolaborasi Real-time (Chat / Editor)
Sinkronisasi state secara real-time antar pengguna menggunakan WebSocket bawaan.

```python
realtime {
    provider = "websockets"
    channels = ["chat-lounge"]
}

component Home():
    doc, updateDoc, isLive = useRealtimeChannel("chat-lounge", "room_1")
    myMessage, setMyMessage = use_state("")

    def handleSend():
        if myMessage == "":
            return
        
        current_messages = doc.messages or []
        updated = current_messages.concat([{"user": "Guest", "text": myMessage}])
        updateDoc("messages", updated)
        setMyMessage("")

    return (
        <UI.Page>
            <UI.Navbar title="Live Chat lounge" />
            <div className="pt-24 max-w-xl mx-auto px-4">
                <UI.Card title={isLive ? "🟢 Online" : "🔴 Offline"}>
                    <div className="h-64 overflow-y-auto space-y-2 p-2 bg-slate-900 rounded border border-slate-800">
                        {doc.messages and doc.messages.map((m, idx) => (
                            <div key={idx} className="p-2 bg-slate-850 rounded">
                                <strong className="text-blue-400">{m.user}:</strong>
                                <span className="ml-2 text-white">{m.text}</span>
                            </div>
                        ))}
                    </div>
                    
                    <div className="flex gap-2 mt-4">
                        <UI.Input value={myMessage} onChange={setMyMessage} placeholder="Ketik pesan..." className="flex-1" />
                        <UI.Button onClick={handleSend}>Kirim</UI.Button>
                    </div>
                </UI.Card>
            </div>
        </UI.Page>
    )

style {
    primary = "#06b6d4"
    radius = "12px"
}
```
