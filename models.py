from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(
    db.String(20),
    default="student"
    )

# Course Table
class Course(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    course = db.Column(db.String(200))

    category = db.Column(db.String(100))

    description = db.Column(db.Text)

    level = db.Column(db.String(50))

    duration = db.Column(db.String(50))

    rating = db.Column(db.Float)

