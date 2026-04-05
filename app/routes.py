# ─── ROUTES / HALAMAN ───
# Semua endpoint aplikasi: dashboard, CRUD siswa, nilai, rapor, export, auth, user management
import os
import uuid
import sqlite3
import csv
import io
import hashlib
from functools import wraps
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    Response,
)
from flask_login import login_user, logout_user, login_required, current_user
from .models import get_db, User
from .config import ALLOWED_EXTENSIONS, MAPEL, KELAS_OPTIONS

main = Blueprint("main", __name__)
PER_PAGE = 10  # Jumlah siswa per halaman


# ─── Decorator: hanya admin ───
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash(
                "Akses ditolak! Hanya admin yang dapat mengakses halaman ini.", "error"
            )
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)

    return decorated


# ─── Decorator: user biasa tidak bisa write (hanya admin) ───
def write_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Akses ditolak! Hanya admin yang dapat melakukan aksi ini.", "error")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)

    return decorated


# ─── HELPER: hash password ───
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ─── LOGIN ───
@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        user_row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)
        ).fetchone()
        conn.close()

        if user_row and user_row["password"] == hash_password(password):
            user = User(user_row)
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page if next_page else url_for("main.dashboard"))
        else:
            flash("Username atau password salah!", "error")

    return render_template("login.html")


# ─── LOGOUT ───
@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.", "success")
    return redirect(url_for("main.login"))


# ─── USER MANAGEMENT (admin only) ───
@main.route("/users")
@login_required
@admin_required
def daftar_users():
    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("users.html", users=users)


@main.route("/users/tambah", methods=["POST"])
@login_required
@admin_required
def tambah_user():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    nama_lengkap = request.form.get("nama_lengkap", "").strip()
    role = request.form.get("role", "user")

    if not username or not password or not nama_lengkap:
        flash("Semua field wajib diisi!", "error")
        return redirect(url_for("main.daftar_users"))

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password, nama_lengkap, role) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), nama_lengkap, role),
        )
        conn.commit()
        flash(f"User '{username}' berhasil ditambahkan!", "success")
    except sqlite3.IntegrityError:
        flash(f"Username '{username}' sudah terdaftar!", "error")
    finally:
        conn.close()

    return redirect(url_for("main.daftar_users"))


@main.route("/users/edit/<int:id>", methods=["POST"])
@login_required
@admin_required
def edit_user(id):
    password = request.form.get("password", "").strip()
    nama_lengkap = request.form.get("nama_lengkap", "").strip()
    role = request.form.get("role", "user")

    if not nama_lengkap:
        flash("Nama lengkap wajib diisi!", "error")
        return redirect(url_for("main.daftar_users"))

    conn = get_db()
    if password:
        conn.execute(
            "UPDATE users SET nama_lengkap = ?, role = ?, password = ? WHERE id = ?",
            (nama_lengkap, role, hash_password(password), id),
        )
    else:
        conn.execute(
            "UPDATE users SET nama_lengkap = ?, role = ? WHERE id = ?",
            (nama_lengkap, role, id),
        )
    conn.commit()
    conn.close()
    flash("User berhasil diperbarui!", "success")
    return redirect(url_for("main.daftar_users"))


@main.route("/users/hapus/<int:id>", methods=["POST"])
@login_required
@admin_required
def hapus_user(id):
    if id == current_user.id:
        flash("Anda tidak bisa menghapus akun sendiri!", "error")
        return redirect(url_for("main.daftar_users"))

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("User berhasil dihapus!", "success")
    return redirect(url_for("main.daftar_users"))


# ─── Cek ekstensi file yang diizinkan ───


# ─── Cek ekstensi file yang diizinkan ───
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ─── Helper pagination sederhana ───
class Pagination:
    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = max(1, (total + per_page - 1) // per_page)
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None

    def iter_pages(self, left=2, right=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left
                or num > self.pages - right
                or (left < num <= self.page + 1)
                or (self.page - 1 < num <= self.pages - right)
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


# ─── DASHBOARD ───
@main.route("/")
@login_required
def dashboard():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM siswa").fetchone()[0]
    laki = conn.execute(
        "SELECT COUNT(*) FROM siswa WHERE jenis_kelamin='L'"
    ).fetchone()[0]
    perempuan = conn.execute(
        "SELECT COUNT(*) FROM siswa WHERE jenis_kelamin='P'"
    ).fetchone()[0]
    kelas_data = conn.execute(
        "SELECT kelas, COUNT(*) as jml FROM siswa GROUP BY kelas"
    ).fetchall()
    siswa_ranking = conn.execute(
        """SELECT s.*, ROUND(AVG(n.nilai_akhir), 1) as rata_rata
           FROM siswa s
           LEFT JOIN nilai n ON s.id = n.siswa_id
           WHERE n.semester = 'Ganjil 2025/2026'
           GROUP BY s.id
           ORDER BY rata_rata DESC
           LIMIT 10"""
    ).fetchall()
    avg_nilai = conn.execute(
        "SELECT s.kelas, ROUND(AVG(n.nilai_akhir),1) as rata FROM siswa s JOIN nilai n ON s.id = n.siswa_id GROUP BY s.kelas"
    ).fetchall()
    conn.close()
    return render_template(
        "dashboard.html",
        total=total,
        laki=laki,
        perempuan=perempuan,
        kelas_data=kelas_data,
        siswa_ranking=siswa_ranking,
        avg_nilai=avg_nilai,
    )


# ─── DAFTAR SISWA (dengan pencarian, filter, pagination) ───
@main.route("/siswa")
@login_required
def daftar_siswa():
    q = request.args.get("q", "")
    kelas_filter = request.args.get("kelas", "")
    page = request.args.get("page", 1, type=int)

    conn = get_db()
    where = []
    params = []

    # ─── Tambahkan filter pencarian ───
    if q:
        where.append("(nama LIKE ? OR nis LIKE ?)")
        params += [f"%{q}%", f"%{q}%"]
    if kelas_filter:
        where.append("kelas = ?")
        params.append(kelas_filter)

    where_sql = " AND ".join(where) if where else "1=1"

    # ─── Hitung total untuk pagination ───
    total = conn.execute(
        f"SELECT COUNT(*) FROM siswa WHERE {where_sql}", params
    ).fetchone()[0]
    pagination = Pagination(page, PER_PAGE, total)

    # ─── Ambil data siswa sesuai halaman ───
    params += [PER_PAGE, (page - 1) * PER_PAGE]
    siswa = conn.execute(
        f"SELECT * FROM siswa WHERE {where_sql} ORDER BY nama LIMIT ? OFFSET ?", params
    ).fetchall()
    kelas_list = conn.execute(
        "SELECT DISTINCT kelas FROM siswa ORDER BY kelas"
    ).fetchall()
    conn.close()

    return render_template(
        "siswa.html",
        siswa=siswa,
        kelas_list=kelas_list,
        q=q,
        kelas_filter=kelas_filter,
        pagination=pagination,
    )


# ─── EXPORT DATA SISWA KE CSV ───
@main.route("/siswa/export")
@login_required
def export_csv():
    if current_user.role != "admin":
        flash("Akses ditolak! Hanya admin yang dapat mengunduh CSV.", "error")
        return redirect(url_for("main.daftar_siswa"))

    conn = get_db()
    siswa = conn.execute("SELECT * FROM siswa ORDER BY nama").fetchall()
    conn.close()

    # ─── Tulis CSV ke StringIO ───
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "NISN",
            "Nama",
            "Kelas",
            "Jenis Kelamin",
            "Tempat Lahir",
            "Tanggal Lahir",
            "Alamat",
            "No. Telepon",
        ]
    )

    for s in siswa:
        # ─── Sensor tanggal lahir (tampilkan tahun-bulan saja) ───
        tgl = s["tanggal_lahir"] or ""
        if tgl:
            parts = str(tgl).split("-")
            tgl = f"{parts[0]}-{parts[1]}-****" if len(parts) == 3 else ""

        # ─── Prefix "=\"" agar Excel tidak mengubah nomor jadi scientific notation ───
        no_telp = '="' + str(s["no_telp"]) + '"' if s["no_telp"] else ""

        writer.writerow(
            [
                s["nis"],
                s["nama"],
                s["kelas"],
                "Laki-laki" if s["jenis_kelamin"] == "L" else "Perempuan",
                s["tempat_lahir"] or "",
                tgl,
                s["alamat"] or "",
                no_telp,
            ]
        )

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=data_siswa.csv"},
    )


# ─── IMPORT DATA DARI CSV ───
@main.route("/siswa/import", methods=["GET", "POST"])
@login_required
@write_required
def import_csv():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Pilih file CSV terlebih dahulu!", "error")
            return redirect(url_for("main.import_csv"))

        try:
            # ─── Baca file CSV ───
            content = file.read().decode("utf-8-sig")  # utf-8-sig support BOM Excel
            reader = csv.DictReader(io.StringIO(content))

            conn = get_db()
            success = 0
            skipped = 0

            for row in reader:
                nis = row.get("NISN", "").strip()
                nama = row.get("Nama", "").strip()
                kelas = row.get("Kelas", "").strip()
                jk = row.get("Jenis Kelamin", "").strip()
                tempat = row.get("Tempat Lahir", "").strip()
                tgl = row.get("Tanggal Lahir", "").strip()
                alamat = row.get("Alamat", "").strip()
                telp = row.get("No. Telepon", "").strip()

                # ─── Validasi field wajib ───
                if not nis or not nama or not kelas:
                    skipped += 1
                    continue

                # ─── Normalisasi jenis kelamin ───
                jk_code = "L" if jk.lower().startswith("l") else "P"

                try:
                    conn.execute(
                        "INSERT INTO siswa (nis,nama,kelas,jenis_kelamin,tempat_lahir,tanggal_lahir,alamat,no_telp) VALUES (?,?,?,?,?,?,?,?)",
                        (nis, nama, kelas, jk_code, tempat, tgl, alamat, telp),
                    )
                    success += 1
                except sqlite3.IntegrityError:
                    skipped += 1  # NISN duplikat

            conn.commit()
            conn.close()

            msg = f"Berhasil import {success} siswa."
            if skipped > 0:
                msg += f" {skipped} data dilewati (duplikat/kurang data)."
            flash(msg, "success")
            return redirect(url_for("main.daftar_siswa"))

        except Exception as e:
            flash(f"Gagal import: {str(e)}", "error")
            return redirect(url_for("main.import_csv"))

    return render_template("import_csv.html")


# ─── TAMBAH SISWA ───
@main.route("/siswa/tambah", methods=["GET", "POST"])
@login_required
@write_required
def tambah_siswa():
    if request.method == "POST":
        foto_filename = _handle_upload(request.files.get("foto"), "default.png")

        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO siswa (nis,nama,kelas,jenis_kelamin,tempat_lahir,tanggal_lahir,alamat,no_telp,foto)
                            VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    request.form["nis"],
                    request.form["nama"],
                    request.form["kelas"],
                    request.form["jenis_kelamin"],
                    request.form["tempat_lahir"],
                    request.form["tanggal_lahir"],
                    request.form["alamat"],
                    request.form["no_telp"],
                    foto_filename,
                ),
            )
            conn.commit()
            flash("Data siswa berhasil ditambahkan!", "success")
            return redirect(url_for("main.daftar_siswa"))
        except sqlite3.IntegrityError:
            flash("NISN sudah terdaftar!", "error")
        finally:
            conn.close()

    return render_template(
        "form_siswa.html", action="tambah", siswa=None, kelas_options=KELAS_OPTIONS
    )


# ─── EDIT SISWA ───
@main.route("/siswa/edit/<int:id>", methods=["GET", "POST"])
@login_required
@write_required
def edit_siswa(id):
    conn = get_db()
    siswa = conn.execute("SELECT * FROM siswa WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        # ─── Pertahankan foto lama jika tidak ada upload baru ───
        foto_filename = _handle_upload(request.files.get("foto"), siswa["foto"])

        conn.execute(
            """UPDATE siswa SET nis=?,nama=?,kelas=?,jenis_kelamin=?,tempat_lahir=?,
                        tanggal_lahir=?,alamat=?,no_telp=?,foto=? WHERE id=?""",
            (
                request.form["nis"],
                request.form["nama"],
                request.form["kelas"],
                request.form["jenis_kelamin"],
                request.form["tempat_lahir"],
                request.form["tanggal_lahir"],
                request.form["alamat"],
                request.form["no_telp"],
                foto_filename,
                id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Data siswa berhasil diperbarui!", "success")
        return redirect(url_for("main.detail_siswa", id=id))

    conn.close()
    return render_template(
        "form_siswa.html", action="edit", siswa=siswa, kelas_options=KELAS_OPTIONS
    )


# ─── HAPUS SISWA ───
@main.route("/siswa/hapus/<int:id>", methods=["POST"])
@login_required
@write_required
def hapus_siswa(id):
    conn = get_db()
    conn.execute("DELETE FROM siswa WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Data siswa berhasil dihapus!", "success")
    return redirect(url_for("main.daftar_siswa"))


# ─── DETAIL SISWA + INPUT NILAI ───
@main.route("/siswa/<int:id>")
@login_required
def detail_siswa(id):
    conn = get_db()
    siswa = conn.execute("SELECT * FROM siswa WHERE id=?", (id,)).fetchone()
    nilai = conn.execute(
        "SELECT * FROM nilai WHERE siswa_id=? AND semester=? ORDER BY mata_pelajaran",
        (id, "Ganjil 2025/2026"),
    ).fetchall()
    semester_list = conn.execute(
        "SELECT DISTINCT semester FROM nilai WHERE siswa_id=? ORDER BY semester", (id,)
    ).fetchall()
    rata_rata = conn.execute(
        "SELECT ROUND(AVG(nilai_akhir),1) as rata FROM nilai WHERE siswa_id=? AND semester=?",
        (id, "Ganjil 2025/2026"),
    ).fetchone()
    conn.close()
    return render_template(
        "detail_siswa.html",
        siswa=siswa,
        nilai=nilai,
        semester_list=semester_list,
        rata_rata=rata_rata,
        mapel_all=MAPEL,
    )


# ─── SIMPAN NILAI RAPOR ───
@main.route("/nilai/simpan/<int:siswa_id>", methods=["POST"])
@login_required
@write_required
def simpan_nilai(siswa_id):
    conn = get_db()
    semester = request.form.get("semester", "Ganjil 2025/2026")

    # ─── Hitung & simpan nilai untuk setiap mata pelajaran ───
    for mapel in MAPEL:
        nh = float(request.form.get(f"nh_{mapel}", 0) or 0)
        nuts = float(request.form.get(f"uts_{mapel}", 0) or 0)
        nuas = float(request.form.get(f"uas_{mapel}", 0) or 0)
        na = round(nh * 0.4 + nuts * 0.3 + nuas * 0.3, 1)

        existing = conn.execute(
            "SELECT id FROM nilai WHERE siswa_id=? AND semester=? AND mata_pelajaran=?",
            (siswa_id, semester, mapel),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE nilai SET nilai_harian=?,nilai_uts=?,nilai_uas=?,nilai_akhir=? WHERE id=?",
                (nh, nuts, nuas, na, existing["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO nilai (siswa_id,semester,mata_pelajaran,nilai_harian,nilai_uts,nilai_uas,nilai_akhir) VALUES (?,?,?,?,?,?,?)",
                (siswa_id, semester, mapel, nh, nuts, nuas, na),
            )

    conn.commit()
    conn.close()
    flash("Nilai rapor berhasil disimpan!", "success")
    return redirect(url_for("main.detail_siswa", id=siswa_id))


# ─── HELPER: Handle upload foto ───
def _handle_upload(file, default):
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        return filename
    return default
