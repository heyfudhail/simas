# SIMAS — Sistem Informasi Manajemen Siswa

Aplikasi web berbasis **Flask (Python)** untuk mengelola data siswa dan nilai rapor secara digital. Dilengkapi sistem login multi-level, pencarian, filter kelas, upload foto, dan ekspor CSV.

---

## Fitur Utama

- **Autentikasi Multi-Level** — Login Admin dan User dengan hak akses berbeda. Password di-hash menggunakan SHA-256.
- **Manajemen Data Siswa** — Tambah, lihat, edit, dan hapus data siswa. Mendukung upload foto profil.
- **Nilai Rapor Digital** — Input nilai Harian (40%), UTS (30%), dan UAS (30%). Nilai akhir dihitung otomatis.
- **Pencarian & Filter** — Cari siswa berdasarkan nama/NISN dan filter berdasarkan kelas.
- **Export CSV** — Admin dapat mengekspor seluruh data siswa ke file CSV.
- **Manajemen User** — Admin dapat menambah, mengedit, dan menonaktifkan akun user.
- **Data Dummy Otomatis** — 50 siswa beserta nilai rapor di-seed otomatis saat pertama kali dijalankan.

---

## Teknologi

| Komponen | Teknologi |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite |
| Template | Jinja2 |
| Autentikasi | Flask-Login |
| Frontend | HTML, CSS, JavaScript |

---

## Struktur Proyek

```
project/
├── main.py                  # Entry point aplikasi
├── seed_data.py             # Script pengisian data dummy
├── data/
│   └── database.db          # File database SQLite
├── static/
│   └── uploads/             # Folder foto siswa
├── templates/
│   ├── base.html
│   ├── siswa.html           # Halaman daftar siswa
│   ├── detail_siswa.html    # Halaman detail & nilai siswa
│   └── users.html           # Halaman manajemen user
└── app/
    ├── __init__.py          # Factory function create_app()
    ├── config.py            # Konfigurasi aplikasi
    ├── models.py            # Koneksi DB, model User, init tabel
    └── routes.py            # Semua route / endpoint
```

---

## Struktur Database

### Tabel `users`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | INTEGER | Primary key |
| username | TEXT | Username unik |
| password | TEXT | SHA-256 hash |
| nama_lengkap | TEXT | Nama lengkap user |
| role | TEXT | `admin` atau `user` |
| is_active | INTEGER | Status aktif |
| created_at | TIMESTAMP | Waktu dibuat |

### Tabel `siswa`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | INTEGER | Primary key |
| nis | TEXT | NISN unik 10 digit |
| nama | TEXT | Nama lengkap siswa |
| kelas | TEXT | X / XI-IPA / XI-IPS / XII-IPA / XII-IPS |
| jenis_kelamin | TEXT | `L` atau `P` |
| tempat_lahir | TEXT | Kota tempat lahir |
| tanggal_lahir | TEXT | Format YYYY-MM-DD |
| alamat | TEXT | Alamat lengkap |
| no_telp | TEXT | Nomor telepon |
| foto | TEXT | Nama file foto (default: `default.png`) |

### Tabel `nilai`
| Kolom | Tipe | Keterangan |
|---|---|---|
| id | INTEGER | Primary key |
| siswa_id | INTEGER | Foreign key ke `siswa.id` |
| semester | TEXT | Contoh: `Ganjil 2025/2026` |
| mata_pelajaran | TEXT | Nama mapel |
| nilai_harian | REAL | Bobot 40% |
| nilai_uts | REAL | Bobot 30% |
| nilai_uas | REAL | Bobot 30% |
| nilai_akhir | REAL | Dihitung otomatis |

**Formula nilai akhir:**
```
Nilai Akhir = (Nilai Harian × 0.4) + (Nilai UTS × 0.3) + (Nilai UAS × 0.3)
```

---

## Mata Pelajaran

Matematika, Bahasa Indonesia, Bahasa Inggris, Informatika, Fisika, Kimia, Biologi, Sejarah, PKN, Olahraga

---

## Cara Menjalankan

### 1. Clone & Install Dependencies

```bash
git clone <repo-url>
cd project
pip install flask flask-login
```

### 2. Jalankan Aplikasi

```bash
python main.py
```

Aplikasi berjalan di `http://localhost:5000`. Database dan data dummy dibuat otomatis saat pertama kali dijalankan.

---

## Akun Default

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `adminaccess123` |
| User | `user` | `useraccess123` |

> **Catatan:** Ganti password default sebelum digunakan di lingkungan produksi.

---

## Hak Akses

| Fitur | Admin | User |
|---|---|---|
| Lihat daftar siswa | ✅ | ✅ |
| Lihat detail & nilai siswa | ✅ | ✅ |
| Tambah / edit / hapus siswa | ✅ | ❌ |
| Input & simpan nilai rapor | ✅ | ❌ |
| Export CSV | ✅ | ❌ |
| Manajemen user | ✅ | ❌ |

---

## Lisensi

Proyek ini dibuat untuk keperluan tugas mata pelajaran Informatika.
