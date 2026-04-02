# 🎓 SIMAS — Sistem Informasi Manajemen Siswa

> Project PTS Informatika · **Fudhail** · Kelas X · 2026

---

## 📌 Tentang Project

**SIMAS** adalah aplikasi web berbasis Python Flask untuk mengelola data siswa dan nilai rapor secara digital. Dirancang untuk memudahkan pencatatan, pengelolaan, dan pencetakan rapor siswa tanpa kertas berlebihan.

---

## ✨ Fitur Utama

| Fitur | Keterangan |
|-------|-----------|
| 📊 Dashboard | Statistik siswa & grafik sebaran kelas |
| 👥 Data Siswa | Tambah, lihat, edit, hapus data siswa |
| 📷 Upload Foto | Foto profil siswa dengan preview |
| 🔍 Pencarian | Cari berdasarkan nama atau NIS |
| 🏫 Filter Kelas | Filter siswa berdasarkan kelas |
| 📄 Pagination | 10 siswa per halaman |
| 📝 Input Nilai | NH, UTS, UAS dengan auto-hitung nilai akhir |
| 📋 Cetak Rapor | Rapor siap print dengan predikat A/B/C/D |
| 📥 Export CSV | Download data siswa ke Excel |
| 📱 Responsive | Tampilan menyesuaikan di HP & tablet |

---

## 🛠️ Programming language / Dependencies

| Teknologi | Fungsi |
|-----------|--------|
| Python 3.10+ | Bahasa pemrograman utama |
| Flask | Framework web (routing & template) |
| SQLite | Database ringan tanpa server |
| Jinja2 | Template engine HTML dinamis |
| HTML5 + CSS3 | Tampilan antarmuka |
| JavaScript | Interaksi (preview foto, hitung nilai) |
| Chart.js | Grafik visualisasi data |
| Font Awesome 6 | Ikon antarmuka |
| Werkzeug | Upload file |

---

## 🚀 Cara Menjalankan

**1. Install Python** (minimal 3.10) → [python.org](https://python.org)

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Jalankan aplikasi**
```bash
python main.py
```

**4. Buka di browser**
```
http://localhost:5000
```

> Database SQLite otomatis dibuat saat pertama kali dijalankan, lengkap dengan data contoh.

---

## 📂 Struktur Folder

```
simas/
├── main.py                  ← Entry point
├── requirements.txt         ← Library Python
├── README.md
│
├── app/
│   ├── __init__.py          ← Factory app Flask
│   ├── config.py            ← Konfigurasi path & konstanta
│   ├── models.py            ← Database: tabel & seed data
│   └── routes.py            ← Semua endpoint/halaman
│
├── data/
│   └── database.db          ← SQLite (auto-dibuat)
│
├── static/
│   ├── css/style.css        ← Styling
│   ├── js/main.js           ← JavaScript
│   └── uploads/             ← Foto siswa
│
└── templates/
    ├── base.html            ← Layout dasar
    ├── dashboard.html       ← Halaman utama & grafik
    ├── siswa.html           ← Daftar siswa + pagination
    ├── form_siswa.html      ← Form tambah/edit
    ├── detail_siswa.html    ← Profil + input nilai
    └── rapor.html           ← Cetak rapor
```

---

## 📐 Rumus Nilai Akhir

```
Nilai Akhir = (Nilai Harian × 40%) + (UTS × 30%) + (UAS × 30%)
```

| Predikat | Rentang |
|----------|---------|
| A | ≥ 90 |
| B | 80 – 89 |
| C | 70 – 79 |
| D | < 70 |

---

## 📜 Lisensi

MIT License — bebas digunakan dan dimodifikasi.

---

## 📚 Referensi

- [Flask Docs](https://flask.palletsprojects.com/)
- [SQLite Docs](https://www.sqlite.org/docs.html)
- [Chart.js Docs](https://www.chartjs.org/docs/)
- [Font Awesome](https://fontawesome.com/icons)
