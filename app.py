from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
from flask import send_file
import openpyxl
import csv
import os
import pytz

app = Flask(__name__)
app.secret_key = "secret123"

# =========================
# KELAS LIST (Sesuai absensi siswa)
# =========================
kelas_list = [
    "X-1","X-2","X-3","X-4","X-5","X-6","X-7","X-8","X-9","X-10",
    "XI Saintek 1","XI Saintek 2","XI Sainkes 1","XI Sainkes 2",
    "XI Sosek 1","XI Sosek 2","XI Soshum 1","XI Soshum 2","XI Soshum 3",
    "XII Saintek 1","XII Saintek 2","XII Sainkes 1","XII Sainkes 2",
    "XII Sosek 1","XII Sosek 2","XII Soshum 1","XII Soshum 2",
    "XII Soshum 3","XII Soshum 4","XII Soshum 5"
]

# =========================
# HALAMAN ABSEN SISWA
# =========================
@app.route("/")
def absen():
    return render_template("absen.html", kelas_list=kelas_list)

# =========================
# PROSES ABSEN SISWA (AJAX)
# =========================
@app.route("/absen", methods=["POST"])
def absen_siswa():
    nama = request.form.get("nama")
    kelas = request.form.get("kelas")
    status = request.form.get("status")
    
    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.now(tz)

    tanggal = now.strftime("%Y-%m-%d")
    jam = now.strftime("%H:%M:%S")

    file = "absensi.csv"
    with open(file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([tanggal, jam, nama, kelas, status])
    
    return jsonify({"success": True})

# =========================
# LOGIN GURU
# =========================
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username=="smancio admin" and password=="smanciojaya123":
            return redirect("/dashboard")
        else:
            return "Login gagal! Username atau password salah."
    return render_template("login.html")

# =========================
# DASHBOARD GURU
# =========================
@app.route("/dashboard")
def dashboard():
    data = []
    if os.path.exists("absensi.csv"):
        with open("absensi.csv","r") as f:
            reader = csv.reader(f)
            for idx,row in enumerate(reader):
                data.append({
                    "id": idx,
                    "tanggal": row[0],
                    "jam": row[1],
                    "nama": row[2],
                    "kelas": row[3],
                    "status": row[4]
                })

    # Statistik
    hadir = sum(1 for d in data if d["status"]=="Hadir")
    izin = sum(1 for d in data if d["status"]=="Izin")
    sakit = sum(1 for d in data if d["status"]=="Sakit")
    alpha = sum(1 for d in data if d["status"]=="Alpha")

    # Filter dari query params
    kelas_filter = request.args.get("kelas","semua")
    status_filter = request.args.get("status","semua")

    if kelas_filter!="semua":
        data = [d for d in data if d["kelas"]==kelas_filter]
    if status_filter!="semua":
        data = [d for d in data if d["status"]==status_filter]

    return render_template("index.html",
                           data=data,
                           hadir=hadir,
                           izin=izin,
                           sakit=sakit,
                           alpha=alpha,
                           kelas_list=kelas_list,
                           kelas_filter=kelas_filter,
                           status_filter=status_filter)

# =========================
# HAPUS DATA (AJAX)
# =========================
@app.route("/hapus/<int:id>", methods=["POST"])
def hapus(id):
    if not os.path.exists("absensi.csv"):
        return jsonify({"success": False})
    rows = []
    with open("absensi.csv","r") as f:
        rows = list(csv.reader(f))
    if id>=len(rows): return jsonify({"success": False})
    rows.pop(id)
    with open("absensi.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return jsonify({"success": True})

# =========================
# EDIT DATA (AJAX)
# =========================
@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    if not os.path.exists("absensi.csv"):
        return jsonify({"success": False})
    rows = []
    with open("absensi.csv","r") as f:
        rows = list(csv.reader(f))
    if id>=len(rows): return jsonify({"success": False})
    rows[id][2] = request.form.get("nama")
    rows[id][3] = request.form.get("kelas")
    rows[id][4] = request.form.get("status")
    with open("absensi.csv","w",newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return jsonify({"success": True})
# =========================
# EXPORT CSV
# =========================
@app.route("/export")
def export():

    file_csv = "absensi.csv"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Data Absensi"

    # header tabel
    ws.append(["Tanggal","Jam","Nama","Kelas","Status"])

    if os.path.exists(file_csv):
        with open(file_csv, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                ws.append(row)

    file_excel = "absensi.xlsx"
    wb.save(file_excel)

    return send_file(file_excel, as_attachment=True, download_name="absensi.xlsx")
# =========================
# JALANKAN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)