from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///absensi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# DATABASE
class Absensi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    kelas = db.Column(db.String(10))
    status = db.Column(db.String(10))
    tanggal = db.Column(db.DateTime)
    jam = db.Column(db.String(10))


# LOGIN
USERNAME = "adminsmancio"
PASSWORD = "smanciojaya123"


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:
            session["login"] = True
            return redirect("/dashboard")

    return render_template("login.html")


# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "login" not in session:
        return redirect("/")

    status_filter = request.args.get("status")

    if status_filter and status_filter != "semua":
        data = Absensi.query.filter_by(status=status_filter)\
            .order_by(Absensi.id.desc()).all()
    else:
        data = Absensi.query.order_by(Absensi.id.desc()).all()

    hadir = Absensi.query.filter_by(status="Hadir").count()
    izin = Absensi.query.filter_by(status="Izin").count()
    sakit = Absensi.query.filter_by(status="Sakit").count()
    alpha = Absensi.query.filter_by(status="Alpha").count()

    return render_template(
        "index.html",
        data=data,
        hadir=hadir,
        izin=izin,
        sakit=sakit,
        alpha=alpha
    )


# ABSEN SISWA
@app.route("/absen", methods=["POST"])
def absen():

    nama = request.form["nama"]
    kelas = request.form["kelas"]
    status = request.form["status"]

    now = datetime.now()

    data = Absensi(
        nama=nama,
        kelas=kelas,
        status=status,
        tanggal=now,
        jam=now.strftime("%H:%M")
    )

    db.session.add(data)
    db.session.commit()

    return redirect("/dashboard")


# HAPUS DATA
@app.route("/hapus/<int:id>")
def hapus(id):

    data = Absensi.query.get_or_404(id)

    db.session.delete(data)
    db.session.commit()

    return redirect("/dashboard")


# LOGOUT
@app.route("/logout")
def logout():

    session.pop("login", None)
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)