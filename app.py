from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import pymysql

pymysql.install_as_MySQLdb()

# Load config
with open('config.json', 'r') as c:
    parameters = json.load(c)['parameters']

app = Flask(__name__)
app.secret_key = 'secretkey'

# DB connection
app.config["SQLALCHEMY_DATABASE_URI"] = parameters['local_uri']
db = SQLAlchemy(app)

# -----------------------------------
# DATABASE MODELS
# -----------------------------------

class Patients(db.Model):
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)


class Doctors(db.Model):
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    doctor_image = db.Column(db.String(200))
    doctor_thumb_image = db.Column(db.String(200))
    gender = db.Column(db.String(20), nullable=False)
    speciality = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    overview = db.Column(db.String(255))
    fee = db.Column(db.Integer, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)


class Appointments(db.Model):
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'))
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(255))


# -----------------------------------
# PATIENT ROUTES
# -----------------------------------

@app.route("/")
def home():
    doctors = Doctors.query.all()
    return render_template("index.html", parameters=parameters, doctors=doctors)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")

        if Patients.query.filter_by(email=email).first():
            return "⚠️ Email already registered!"

        if Patients.query.filter_by(phone_number=phone_number).first():
            return "⚠️ Phone already registered!"

        entry = Patients(name=name, email=email, phone_number=phone_number, password=password)
        db.session.add(entry)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html", parameters=parameters)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = Patients.query.filter_by(email=email, password=password).first()

        if user:
            session['email'] = user.email
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html", parameters=parameters)


@app.route("/dashboard")
def dashboard():
    if 'email' not in session:
        return redirect(url_for("login"))

    user = Patients.query.filter_by(email=session['email']).first()
    doctors = Doctors.query.all()

    return render_template("user-dashboard.html", user=user, doctors=doctors)


@app.route("/logout")
def logout():
    session.pop('email', None)
    session.pop('admin', None)
    return redirect(url_for("home"))


# -----------------------------------
# DOCTOR PROFILE
# -----------------------------------

@app.route("/doctor-profile/<string:slug>")
def doctor_profile(slug):
    doctor = Doctors.query.filter_by(slug=slug).first()
    if not doctor:
        return "Doctor not found", 404
    return render_template("doctor-profile.html", doctor=doctor)


# -----------------------------------
# BOOKING
# -----------------------------------

@app.route("/booking/<string:slug>", methods=["GET", "POST"])
def booking(slug):
    if 'email' not in session:
        return redirect(url_for("login"))

    doctor = Doctors.query.filter_by(slug=slug).first()
    user = Patients.query.filter_by(email=session['email']).first()

    if request.method == "POST":
        date = request.form.get("date")
        time = request.form.get("time")
        message = request.form.get("message")

        new_booking = Appointments(
            patient_id=user.patient_id,
            doctor_id=doctor.doctor_id,
            date=date,
            time=time,
            message=message,
        )
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for("booking_success"))

    return render_template("booking.html", doctor=doctor)


@app.route("/booking-success")
def booking_success():
    return render_template("booking-success.html")


# -----------------------------------
# ADMIN ROUTES (FINAL WORKING)
# -----------------------------------

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin-dashboard")
        else:
            return render_template("admin-login.html", error="Invalid admin credentials")

    return render_template("admin-login.html")


@app.route("/admin-dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin-login")

    doctors = Doctors.query.all()
    patients = Patients.query.all()
    appointments = Appointments.query.all()

    return render_template("admin-dashboard.html",
                           doctors=doctors,
                           patients=patients,
                           appointments=appointments)


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin-login")


# -----------------------------------
# RUN SERVER
# -----------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
