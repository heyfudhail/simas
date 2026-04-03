# ─── FACTORY APP ───
# Fungsi create_app() untuk membuat instance Flask + register blueprint
from flask import Flask
from .config import SECRET_KEY, UPLOAD_FOLDER
from .models import init_db
import os


def create_app():
    # Setup Flask dengan folder template & static di root project
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = SECRET_KEY
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Buat folder upload & inisialisasi database
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    init_db()

    # ─── Isi data dummy jika database masih kosong ───
    from .models import get_db as _get_db
    _conn = _get_db()
    _empty = _conn.execute("SELECT COUNT(*) FROM siswa").fetchone()[0] == 0
    _conn.close()
    if _empty:
        import sys
        import importlib.util
        _seed_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "seed_data.py")
        _spec = importlib.util.spec_from_file_location("seed_data", _seed_path)
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        _mod.seed_data()

    # Register semua route dari blueprint 'main'
    from .routes import main

    app.register_blueprint(main)

    return app
