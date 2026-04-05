# ─── DATABASE & MODEL ───
# Fungsi koneksi database & inisialisasi tabel (kosong, tanpa data contoh)
import sqlite3
from flask_login import UserMixin
from .config import DATABASE


# ─── Koneksi ke database ───
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Akses kolom via nama (row['nama'])
    return conn


# ─── User class untuk Flask-Login ───
class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.role = row["role"]
        self.nama_lengkap = row["nama_lengkap"]
        self._is_active = bool(row["is_active"])

    @property
    def is_active(self):
        return self._is_active


# ─── Load user by ID untuk Flask-Login ───
def load_user_by_id(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return User(row)
    return None


# ─── Buat tabel jika belum ada (database kosong) ───
def init_db():
    conn = get_db()

    # ─── Buat tabel users, siswa & nilai jika belum ada ───
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nama_lengkap TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
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


# ─── Seed user default jika belum ada ───
def seed_users():
    import hashlib

    conn = get_db()
    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing == 0:

        def hash_pw(pw):
            return hashlib.sha256(pw.encode()).hexdigest()

        conn.execute(
            "INSERT INTO users (username, password, nama_lengkap, role) VALUES (?, ?, ?, ?)",
            ("admin", hash_pw("adminaccess123"), "Administrator", "admin"),
        )
        conn.execute(
            "INSERT INTO users (username, password, nama_lengkap, role) VALUES (?, ?, ?, ?)",
            ("user", hash_pw("useraccess123"), "User Biasa", "user"),
        )
        conn.commit()
    else:

        def hash_pw(pw):
            return hashlib.sha256(pw.encode()).hexdigest()

        conn.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hash_pw("adminaccess123"), "admin"),
        )
        conn.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hash_pw("useraccess123"), "user"),
        )
        conn.commit()
    conn.close()
