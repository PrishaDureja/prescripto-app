from app import db, Doctors, app

with app.app_context():
    d1 = Doctors(
        name="Dr. Aisha Verma",
        doctor_image="admin-assets/img/doctor-1.jpg",
        doctor_thumb_image="admin-assets/img/doctor-thumb-1.jpg",
        gender="Female",
        speciality="Dermatologist",
        department="Skin Care",
        location="Delhi",
        overview="Expert dermatologist with 10 years of experience.",
        fee=500,
        slug="dr-aisha-verma"
    )

    d2 = Doctors(
        name="Dr. Rahul Sharma",
        doctor_image="admin-assets/img/doctor-2.jpg",
        doctor_thumb_image="admin-assets/img/doctor-thumb-2.jpg",
        gender="Male",
        speciality="Cardiologist",
        department="Heart Care",
        location="Mumbai",
        overview="Specialist in cardiovascular medicine.",
        fee=700,
        slug="dr-rahul-sharma"
    )

    db.session.add_all([d1, d2])
    db.session.commit()

    print("Doctors added successfully!")
