from flask import Flask, render_template, request, redirect, session, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import io
import os

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///absensi.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================
# MODEL DATABASE
# =========================
class Absensi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    kelas = db.Column(db.String(20))
    status = db.Column(db.String(20))
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# HALAMAN UTAMA
# =========================
@app.route("/")
def home():
    return redirect("/absen")


# =========================
# ABSEN SISWA
# =========================
@app.route("/absen", methods=["GET","POST"])
def absen():

    if request.method == "POST":

        nama = request.form["nama"]
        kelas = request.form["kelas"]
        status = request.form["status"]

        data = Absensi(
            nama=nama,
            kelas=kelas,
            status=status
        )

        db.session.add(data)
        db.session.commit()

        flash("Absensi berhasil!")

        return redirect("/absen")

    return render_template("absen.html")


# =========================
# LOGIN GURU
# =========================
@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "guru" and password == "123":

            session["login"] = True
            return redirect("/dashboard")

        else:
            flash("Username atau password salah")

    return render_template("login.html")


# =========================
# DASHBOARD GURU
# =========================
@app.route("/dashboard")
def dashboard():

    if "login" not in session:
        return redirect("/login")

    data = Absensi.query.order_by(Absensi.tanggal.desc()).all()

    return render_template("index.html", data=data)


# =========================
# HAPUS DATA
# =========================
@app.route("/hapus/<int:id>")
def hapus(id):

    if "login" not in session:
        return redirect("/login")

    data = Absensi.query.get(id)

    if data:
        db.session.delete(data)
        db.session.commit()

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

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(
        output,
        download_name="absensi_siswa.xlsx",
        as_attachment=True
    )


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.pop("login", None)

    return redirect("/login")


# =========================
# INIT DATABASE
# =========================
with app.app_context():
    db.create_all()


# =========================
# RUN APP (RAILWAY FIX)
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )