from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///absensi.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# DATABASE
# =========================
class Absensi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    kelas = db.Column(db.String(50))
    status = db.Column(db.String(20))
    tanggal = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()

# =========================
# HALAMAN ABSEN SISWA
# =========================
@app.route("/", methods=["GET", "POST"])
def absen():

    if request.method == "POST":

        nama = request.form.get("nama")
        kelas = request.form.get("kelas")
        status = request.form.get("status")

        data = Absensi(
            nama=nama,
            kelas=kelas,
            status=status
        )

        db.session.add(data)
        db.session.commit()

        flash("Absen berhasil!")

        return redirect("/")

    return render_template("absen.html")


# =========================
# LOGIN GURU
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "smanciojaya123":

            session["login"] = True

            return redirect("/dashboard")

        else:
            flash("Username atau Password salah")

    return render_template("login.html")


# =========================
# DASHBOARD GURU
# =========================
@app.route("/dashboard")
def dashboard():

    if "login" not in session:
        return redirect("/login")

    status_filter = request.args.get("status", "semua")

    if status_filter == "semua":
        data = Absensi.query.order_by(Absensi.tanggal.desc()).all()
    else:
        data = Absensi.query.filter_by(status=status_filter).order_by(Absensi.tanggal.desc()).all()

    return render_template("index.html", data=data, status_filter=status_filter)


# =========================
# HAPUS DATA
# =========================
@app.route("/hapus/<int:id>")
def hapus(id):

    if "login" not in session:
        return redirect("/login")

    data = Absensi.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()

    flash("Data berhasil dihapus")

    return redirect("/dashboard")


# =========================
# EXPORT EXCEL
# =========================
@app.route("/export")
def export():

    if "login" not in session:
        return redirect("/login")

    data = Absensi.query.all()

    hasil = []

    for d in data:
        hasil.append({
            "Nama": d.nama,
            "Kelas": d.kelas,
            "Status": d.status,
            "Tanggal": d.tanggal.strftime("%d-%m-%Y %H:%M")
        })

    df = pd.DataFrame(hasil)

    file = "absensi.xlsx"
    df.to_excel(file, index=False)

    return "File Excel berhasil dibuat."


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.pop("login", None)

    return redirect("/login")


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)