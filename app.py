from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import pandas as pd

app = Flask(__name__)
app.secret_key = "smancio_secret"

# ========================
# DATABASE SETUP
# ========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///absensi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Absensi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    kelas = db.Column(db.String(50))
    tanggal = db.Column(db.DateTime)
    jam = db.Column(db.String(10))
    status = db.Column(db.String(10))

with app.app_context():
    db.create_all()

# ========================
# KONSTANT LOGIN
# ========================
USERNAME = "smancio admin"
PASSWORD = "smanciojaya123"

# ========================
# HALAMAN ABSEN SISWA
# ========================
@app.route("/", methods=["GET", "POST"])
def absen():
    if request.method == "POST":
        nama = request.form.get("nama")
        kelas = request.form.get("kelas")
        status = request.form.get("status")
        now = datetime.now()
        absen_data = Absensi(
            nama=nama,
            kelas=kelas,
            tanggal=now,
            jam=now.strftime("%H:%M"),
            status=status
        )
        db.session.add(absen_data)
        db.session.commit()
        return render_template("berhasil.html")
    return render_template("absen.html")

# ========================
# LOGIN GURU
# ========================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == USERNAME and password == PASSWORD:
            return redirect(url_for("dashboard"))
        else:
            return "Login gagal! Username atau password salah."
    return render_template("login.html")

# ========================
# DASHBOARD GURU
# ========================
@app.route("/dashboard")
def dashboard():
    kelas_filter = request.args.get("kelas", "semua")
    status_filter = request.args.get("status", "semua")

    query = Absensi.query
    if kelas_filter != "semua":
        query = query.filter_by(kelas=kelas_filter)
    if status_filter != "semua":
        query = query.filter_by(status=status_filter)

    data = query.order_by(Absensi.tanggal.desc(), Absensi.jam.desc()).all()

    # Statistik
    hadir = Absensi.query.filter_by(status="Hadir").count()
    izin = Absensi.query.filter_by(status="Izin").count()
    sakit = Absensi.query.filter_by(status="Sakit").count()
    alpha = Absensi.query.filter_by(status="Alpha").count()

    return render_template("index.html", data=data, hadir=hadir, izin=izin, sakit=sakit, alpha=alpha)

# ========================
# DASHBOARD DATA (AJAX)
# ========================
@app.route("/dashboard-data")
def dashboard_data():
    data = Absensi.query.order_by(Absensi.tanggal.desc(), Absensi.jam.desc()).all()
    rows = ""
    for siswa in data:
        rows += f"""
        <tr>
        <td>{siswa.nama}</td>
        <td>{siswa.kelas}</td>
        <td>{siswa.tanggal.strftime("%d-%m-%Y")}</td>
        <td>{siswa.jam}</td>
        <td class="status-{siswa.status.lower()}">{siswa.status}</td>
        <td class="aksi">
            <a href='/edit/{siswa.id}'><button class='edit'>✏️ Edit</button></a>
            <a href='/hapus/{siswa.id}'><button class='hapus'>🗑 Hapus</button></a>
        </td>
        </tr>
        """
    return rows

# ========================
# EDIT DATA
# ========================
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    absen = Absensi.query.get_or_404(id)
    if request.method == "POST":
        absen.nama = request.form.get("nama")
        absen.kelas = request.form.get("kelas")
        absen.status = request.form.get("status")
        db.session.commit()
        return redirect(url_for("dashboard"))
    return render_template("edit.html", absen=absen)

# ========================
# HAPUS DATA
# ========================
@app.route("/hapus/<int:id>")
def hapus(id):
    absen = Absensi.query.get_or_404(id)
    db.session.delete(absen)
    db.session.commit()
    return redirect(url_for("dashboard"))

# ========================
# EXPORT EXCEL
# ========================
@app.route("/export")
def export():
    data = Absensi.query.all()
    df = pd.DataFrame([{
        "Nama": x.nama,
        "Kelas": x.kelas,
        "Tanggal": x.tanggal.strftime("%d-%m-%Y"),
        "Jam": x.jam,
        "Status": x.status
    } for x in data])
    file_path = "absensi_export.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

# ========================
# JALANKAN SERVER
# ========================
if __name__ == "__main__":
    app.run(debug=True)