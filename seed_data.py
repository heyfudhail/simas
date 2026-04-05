# ─── SEED DATA ───
# Mengisi database dengan 50 siswa dummy beserta nilai untuk keperluan testing
import sqlite3
import random
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "data", "database.db")

SEMESTER = "Ganjil 2025/2026"

MAPEL = [
    "Matematika",
    "Bahasa Indonesia",
    "Bahasa Inggris",
    "Informatika",
    "Fisika",
    "Kimia",
    "Biologi",
    "Sejarah",
    "PKN",
    "Olahraga",
]

KELAS_OPTIONS = ["X", "XI-IPA", "XI-IPS", "XII-IPA", "XII-IPS"]

# Data Nama
NAMA_DEPAN_L = [
    "Ahmad", "Budi", "Dani", "Eko", "Fajar", "Gilang", "Hendra", "Irfan",
    "Joko", "Kevin", "Lukman", "Muhammad", "Nanda", "Oscar", "Putra",
    "Rafi", "Sandi", "Taufik", "Umar", "Wahyu", "Yusuf", "Zaki",
    "Arif", "Bagas", "Dimas", "Farel", "Galih", "Hafiz",
]

NAMA_DEPAN_P = [
    "Ayu", "Bella", "Citra", "Dewi", "Elsa", "Fitri", "Gita", "Hana",
    "Indah", "Julia", "Kartika", "Lina", "Maya", "Nisa", "Putri",
    "Rina", "Sari", "Tika", "Ulfa", "Vina", "Wulan", "Yuni",
    "Anisa", "Bunga", "Dina", "Fani", "Grace",
]

NAMA_BELAKANG = [
    "Pratama", "Santoso", "Wijaya", "Kusuma", "Rahayu", "Setiawan",
    "Hidayat", "Nugroho", "Saputra", "Wibowo", "Purnama", "Susanto",
    "Hartono", "Gunawan", "Permana", "Lestari", "Anggraini", "Safitri",
    "Maharani", "Utami", "Handayani", "Kurniawan", "Firmansyah",
    "Ramadhan", "Maulana", "Hakim", "Fauzi", "Rizki",
]

KOTA = [
    "Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Semarang",
    "Medan", "Makassar", "Palembang", "Denpasar", "Malang",
    "Bogor", "Depok", "Tangerang", "Bekasi", "Solo",
]

ALAMAT_JALAN = [
    "Jl. Merdeka", "Jl. Sudirman", "Jl. Diponegoro", "Jl. Gatot Subroto",
    "Jl. Ahmad Yani", "Jl. Pahlawan", "Jl. Veteran", "Jl. Pemuda",
    "Jl. Kartini", "Jl. Imam Bonjol", "Jl. Hasanuddin", "Jl. Sisingamangaraja",
]


def seed_data():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    # ─── Cek apakah sudah ada data ───
    existing = conn.execute("SELECT COUNT(*) FROM siswa").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    print("Seeding 50 dummy students...")

    random.seed(42)  # Reproducible results

    siswa_list = []

    # ─── Generate 50 siswa ───
    used_nis = set()
    nama_depan_l = NAMA_DEPAN_L.copy()
    nama_depan_p = NAMA_DEPAN_P.copy()
    random.shuffle(nama_depan_l)
    random.shuffle(nama_depan_p)

    # 25 laki-laki, 25 perempuan
    for i in range(50):
        jk = "L" if i < 25 else "P"

        if jk == "L":
            depan = nama_depan_l[i % len(nama_depan_l)]
        else:
            depan = nama_depan_p[(i - 25) % len(nama_depan_p)]

        belakang = NAMA_BELAKANG[i % len(NAMA_BELAKANG)]
        nama = f"{depan} {belakang}"

        # ─── Generate NISN unik 10 digit ───
        while True:
            nis = str(random.randint(1000000000, 9999999999))
            if nis not in used_nis:
                used_nis.add(nis)
                break

        kelas = KELAS_OPTIONS[i % len(KELAS_OPTIONS)]
        tempat_lahir = random.choice(KOTA)

        # ─── Tanggal lahir antara 2005-2009 ───
        tahun = random.randint(2005, 2009)
        bulan = random.randint(1, 12)
        hari = random.randint(1, 28)
        tanggal_lahir = f"{tahun}-{bulan:02d}-{hari:02d}"

        # ─── Nomor telepon ───
        no_telp = "08" + str(random.randint(100000000, 999999999))

        # ─── Alamat ───
        jalan = random.choice(ALAMAT_JALAN)
        no_rumah = random.randint(1, 150)
        kota = random.choice(KOTA)
        alamat = f"{jalan} No. {no_rumah}, {kota}"

        siswa_list.append((nis, nama, kelas, jk, tempat_lahir, tanggal_lahir, alamat, no_telp))

    # ─── Insert siswa ke database ───
    conn.executemany(
        "INSERT INTO siswa (nis, nama, kelas, jenis_kelamin, tempat_lahir, tanggal_lahir, alamat, no_telp) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        siswa_list,
    )
    conn.commit()

    # ─── Ambil ID siswa yang baru diinsert ───
    siswa_rows = conn.execute("SELECT id FROM siswa ORDER BY id").fetchall()

    # ─── Generate nilai untuk setiap siswa ───
    nilai_list = []
    for row in siswa_rows:
        siswa_id = row["id"]
        for mapel in MAPEL:
            nh = round(random.uniform(65, 98), 1)
            nuts = round(random.uniform(60, 98), 1)
            nuas = round(random.uniform(60, 98), 1)
            na = round(nh * 0.4 + nuts * 0.3 + nuas * 0.3, 1)
            nilai_list.append((siswa_id, SEMESTER, mapel, nh, nuts, nuas, na))

    conn.executemany(
        "INSERT INTO nilai (siswa_id, semester, mata_pelajaran, nilai_harian, nilai_uts, nilai_uas, nilai_akhir) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        nilai_list,
    )
    conn.commit()
    conn.close()

    print(f"Done! Inserted {len(siswa_list)} students with {len(nilai_list)} grade records.")


if __name__ == "__main__":
    seed_data()
