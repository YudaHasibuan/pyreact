# PyReact Production Deployment Guide

Dokumen ini menjelaskan cara menyebarkan aplikasi PyReact Anda ke lingkungan produksi.

## Struktur Deployment
Aplikasi dideploy menggunakan arsitektur dual-process:
1. **Nginx** (Port 80): Melayani static assets frontend React secara instan dan bertindak sebagai Reverse Proxy untuk backend API.
2. **Gunicorn** (Port 5000): Menjalankan Flask backend WSGI server untuk merespons RPC calls dari frontend secara efisien.

## Opsi 1: Menggunakan Docker (Rekomendasi)
Anda dapat mem-build dan menjalankan aplikasi di dalam container Docker.

1. Jalankan perintah build dari root direktori output:
   ```bash
   docker build -f deployment/Dockerfile -t pyreact-app .
   ```

2. Jalankan container:
   ```bash
   docker run -p 8080:80 pyreact-app
   ```
   Buka `http://localhost:8080` pada browser Anda.

## Opsi 2: Menggunakan Fly.io
Fly.io mendukung deployment Dockerfile secara out-of-the-box.

1. Install Fly CLI dan login:
   ```bash
   fly auth login
   ```

2. Inisialisasi fly app:
   ```bash
   fly launch --copy-config
   ```

3. Deploy aplikasi:
   ```bash
   fly deploy
   ```
