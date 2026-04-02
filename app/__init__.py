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

    # Register semua route dari blueprint 'main'
    from .routes import main

    app.register_blueprint(main)

    return app
