# ─── KONFIGURASI APLIKASI ───
# Semua pengaturan utama: folder upload, database, mata pelajaran, dll.
import os

# Path root project (sistem_siswa/)
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# Secret key untuk session Flask
SECRET_KEY = "simas_secret_key_2025"

# Folder untuk menyimpan foto siswa
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Lokasi database SQLite
DATABASE = os.path.join(BASE_DIR, "data", "database.db")

# Daftar mata pelajaran yang diajarkan
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

# Opsi kelas: X tanpa jurusan, XI & XII dengan IPA/IPS
KELAS_OPTIONS = ["X", "XI-IPA", "XI-IPS", "XII-IPA", "XII-IPS"]
