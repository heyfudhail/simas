# ─── ROUTES / HALAMAN ───
# Semua endpoint aplikasi: dashboard, CRUD siswa, nilai, rapor, export
import os
import uuid
import sqlite3
import csv
import io
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
from .models import get_db
from .config import ALLOWED_EXTENSIONS, MAPEL, KELAS_OPTIONS

main = Blueprint("main", __name__)
PER_PAGE = 10  # Jumlah siswa per halaman


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
    siswa_terbaru = conn.execute(
        "SELECT * FROM siswa ORDER BY created_at DESC LIMIT 5"
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
        siswa_terbaru=siswa_terbaru,
        avg_nilai=avg_nilai,
    )


# ─── DAFTAR SISWA (dengan pencarian, filter, pagination) ───
@main.route("/siswa")
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
def export_csv():
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
def hapus_siswa(id):
    conn = get_db()
    conn.execute("DELETE FROM siswa WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Data siswa berhasil dihapus!", "success")
    return redirect(url_for("main.daftar_siswa"))


# ─── DETAIL SISWA + INPUT NILAI ───
@main.route("/siswa/<int:id>")
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


# ─── CETAK RAPOR ───
@main.route("/rapor/<int:id>")
def cetak_rapor(id):
    conn = get_db()
    siswa = conn.execute("SELECT * FROM siswa WHERE id=?", (id,)).fetchone()
    nilai = conn.execute(
        "SELECT * FROM nilai WHERE siswa_id=? AND semester=? ORDER BY mata_pelajaran",
        (id, "Ganjil 2025/2026"),
    ).fetchall()
    rata_rata = conn.execute(
        "SELECT ROUND(AVG(nilai_akhir),1) as rata FROM nilai WHERE siswa_id=? AND semester=?",
        (id, "Ganjil 2025/2026"),
    ).fetchone()
    conn.close()
    return render_template("rapor.html", siswa=siswa, nilai=nilai, rata_rata=rata_rata)


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
