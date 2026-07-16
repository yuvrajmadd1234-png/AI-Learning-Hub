from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User, Course
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)

# Login Page
@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["role"] = user.role
            return redirect(url_for("dashboard.dashboard"))
            

        else:
            return "<h2>❌ Invalid Email or Password</h2><br><a href='/login'>Try Again</a>"

    return render_template("login.html")

# Register Page
@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return """
            <h2>❌ Email already registered!</h2>
            <br>
            <a href='/register'>Try Another Email</a>
            """

        hashed_password = generate_password_hash(password)
        
        role = "student"

        if email == "admin@gmail.com":
            role = "admin"

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(new_user)
        db.session.commit()

        return "<h2>Registration Successful! 🎉</h2><br><a href='/login'>Go to Login</a>"

    return render_template("register.html")

@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))