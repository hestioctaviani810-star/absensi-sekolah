from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import csv
import os

app = Flask(__name__)
app.secret_key = "secret123"

CSV_FILE = "absensi.csv"

# ========================
# HALAMAN ABSEN SISWA
# ========================
@app.route("/")
def absen():
    return render_template("absen.html")

@app.route("/absen", methods=["POST"])
def proses_absen():
    nama = request.form.get("nama")
    kelas = request.form.get("kelas")
    status = request.form.get("status")

    tanggal = datetime.now().strftime("%Y-%m-%d")
    jam = datetime.now().strftime("%H:%M:%S")

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([nama, kelas, tanggal, jam, status])

    return render_template("berhasil.html")


# ========================
# LOGIN GURU
# ========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "smancio admin" and password == "smanciojaya123":
            return redirect(url_for("dashboard"))
        else:
            return "Login gagal! Username atau password salah."
    return render_template("login.html")


# ========================
# DASHBOARD GURU
# ========================
@app.route("/dashboard")
def dashboard():
    kelas_list = [
        "X-1","X-2","X-3","X-4","X-5","X-6","X-7","X-8","X-9","X-10",
        "XI Saintek 1","XI Saintek 2","XI Sainkes 1","XI Sainkes 2",
        "XI Sosek 1","XI Sosek 2","XI Soshum 1","XI Soshum 2","XI Soshum 3",
        "XII Saintek 1","XII Saintek 2","XII Sainkes 1","XII Sainkes 2",
        "XII Sosek 1","XII Sosek 2","XII Soshum 1","XII Soshum 2","XII Soshum 3","XII Soshum 4","XII Soshum 5"
    ]
    status_list = ["Hadir","Izin","Sakit","Alpha"]
    return render_template("index.html", kelas_list=kelas_list, status_list=status_list)


# ========================
# API UNTUK RELOAD DATA + FILTER + STATISTIK
# ========================
@app.route("/api/data")
def api_data():
    kelas_filter = request.args.get("kelas", "")
    status_filter = request.args.get("status", "")

    data = []
    statistik = {"Hadir":0, "Izin":0, "Sakit":0, "Alpha":0}

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 5:
                    nama, kelas, tanggal, jam, status = row
                    if (kelas_filter == "" or kelas_filter == kelas) and \
                       (status_filter == "" or status_filter == status):
                        data.append({
                            "nama": nama,
                            "kelas": kelas,
                            "tanggal": tanggal,
                            "jam": jam,
                            "status": status
                        })
                        if status in statistik:
                            statistik[status] += 1

    return jsonify({"data":data, "statistik":statistik})


# ========================
# HAPUS DATA
# ========================
@app.route("/hapus/<nama>/<kelas>/<tanggal>/<jam>")
def hapus(nama, kelas, tanggal, jam):
    rows = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row != [nama, kelas, tanggal, jam, row[4]]:
                    rows.append(row)
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)