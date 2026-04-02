# ─── DATABASE & MODEL ───
# Fungsi koneksi database & inisialisasi tabel (kosong, tanpa data contoh)
import sqlite3
from .config import DATABASE


# ─── Koneksi ke database ───
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Akses kolom via nama (row['nama'])
    return conn


# ─── Buat tabel jika belum ada (database kosong) ───
def init_db():
    conn = get_db()

    # ─── Buat tabel siswa & nilai jika belum ada ───
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nis TEXT UNIQUE NOT NULL,
            nama TEXT NOT NULL,
            kelas TEXT NOT NULL,
            jenis_kelamin TEXT NOT NULL,
            tempat_lahir TEXT,
            tanggal_lahir TEXT,
            alamat TEXT,
            no_telp TEXT,
            foto TEXT DEFAULT 'default.png',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS nilai (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siswa_id INTEGER NOT NULL,
            semester TEXT NOT NULL,
            mata_pelajaran TEXT NOT NULL,
            nilai_harian REAL DEFAULT 0,
            nilai_uts REAL DEFAULT 0,
            nilai_uas REAL DEFAULT 0,
            nilai_akhir REAL DEFAULT 0,
            FOREIGN KEY (siswa_id) REFERENCES siswa(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
