from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.metrics.pairwise import cosine_similarity
app = Flask(__name__)

app.secret_key = "your_super_secret_key"

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# Course Table
class Course(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    course = db.Column(db.String(200))

    category = db.Column(db.String(100))

    description = db.Column(db.Text)

    level = db.Column(db.String(50))

    duration = db.Column(db.String(50))

    rating = db.Column(db.Float)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id

            session["user_name"] = user.name

            courses = Course.query.all()

            total_courses = len(courses)

            average_rating = round(
                sum(c.rating for c in courses) / total_courses,
                1
            ) if total_courses else 0

            total_categories = len(set(c.category for c in courses))

            return redirect(url_for("dashboard"))
            

        else:
            return "<h2>❌ Invalid Email or Password</h2><br><a href='/login'>Try Again</a>"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    courses = Course.query.all()

    total_courses = len(courses)

    average_rating = round(
        sum(c.rating for c in courses) / total_courses,
        1
    ) if total_courses else 0

    total_categories = len(set(c.category for c in courses))

    return render_template(
        "dashboard.html",
        user=user,
        total_courses=total_courses,
        average_rating=average_rating,
        total_categories=total_categories
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    return render_template(
        "profile.html",
        user=user
    )

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = db.session.get(User, session["user_id"])

    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]

        db.session.commit()

        return redirect(url_for("profile"))

    return render_template(
        "edit_profile.html",
        user=user
    )

@app.route("/courses_page")
def courses_page():
    return render_template("courses.html")


@app.route("/about")
def about():
    return render_template("about.html")

# Register Page
@app.route("/register", methods=["GET", "POST"])
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
        
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return "<h2>Registration Successful! 🎉</h2><br><a href='/login'>Go to Login</a>"

    return render_template("register.html")

@app.route("/users")
def users():
    all_users = User.query.all()
    return render_template("users.html", users=all_users)
@app.route("/recommend", methods=["POST"])
def recommend():

    interest = request.form["interest"]

    # Read courses from SQLite
    courses = Course.query.all()

    df = pd.DataFrame([
        {
            "Course": c.course,
            "Category": c.category,
            "Description": c.description,
            "Level": c.level,
            "Duration": c.duration,
            "Rating": c.rating
        }
        for c in courses
    ])

    if df.empty:
        return render_template(
            "recommendation.html",
            interest=interest,
            courses=[]
        )

    # Create content column
    df["content"] = df["Category"] + " " + df["Description"]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df["content"])

    similarity = cosine_similarity(tfidf_matrix)

    selected = df[df["Category"] == interest]

    if selected.empty:
        return render_template(
            "recommendation.html",
            interest=interest,
            courses=[]
        )

    selected_index = selected.index[0]

    scores = list(enumerate(similarity[selected_index]))

    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recommended = []

    for index, score in scores[:4]:

        course = df.iloc[index].to_dict()

        course["Match"] = round(score * 100)

        recommended.append(course)

    return render_template(
        "recommendation.html",
        interest=interest,
        courses=recommended
    )

@app.route("/search", methods=["POST"])
def search():

    query = request.form["query"]

    courses = Course.query.all()

    df = pd.DataFrame([
        {
            "Course": c.course,
            "Category": c.category,
            "Description": c.description,
            "Level": c.level,
            "Duration": c.duration,
            "Rating": c.rating
        }
        for c in courses
    ])

    result = df[
        df["Course"].str.contains(query, case=False, na=False)
    ]

    courses = result.to_dict(orient="records")

    return render_template(
        "recommendation.html",
        interest=query,
        courses=courses
    )

@app.route("/add_course", methods=["POST"])
def add_course():

    new_course = Course(
        course=request.form["course"],
        category=request.form["category"],
        description=request.form["description"],
        level=request.form["level"],
        duration=request.form["duration"],
        rating=float(request.form["rating"])
    )

    db.session.add(new_course)
    db.session.commit()

    return """
    <h2>✅ Course Added Successfully!</h2>

    <br>

    <a href="/admin">Add Another Course</a>

    <br><br>

    <a href="/">Home</a>
    """

@app.route("/import")
def import_courses():

    # Prevent duplicate imports
    if Course.query.count() > 0:
        return "<h2>Courses already imported.</h2>"

    df = pd.read_csv("data/courses.csv")

    for _, row in df.iterrows():

        course = Course(
            course=row["Course"],
            category=row["Category"],
            description=row["Description"],
            level=row["Level"],
            duration=row["Duration"],
            rating=float(row["Rating"])
        )

        db.session.add(course)

    db.session.commit()

    return "<h2>✅ Courses Imported Successfully!</h2>"

@app.route("/courses")
def courses():

    all_courses = Course.query.all()

    html = "<h2>Courses in Database</h2><hr>"

    for c in all_courses:
        html += f"<p>{c.course} | {c.category} | ⭐ {c.rating}</p>"

    return html

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)