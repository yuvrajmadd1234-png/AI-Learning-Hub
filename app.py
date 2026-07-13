from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from models import db, User, Course
from routes.dashboard import dashboard_bp
from routes.auth import auth
from utils import login_required
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.metrics.pairwise import cosine_similarity
from routes.courses import courses_bp
from routes.profile import profile_bp

app = Flask(__name__)

app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(auth)

app.register_blueprint(dashboard_bp)

app.register_blueprint(courses_bp)

app.register_blueprint(profile_bp)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/courses_page")
def courses_page():
    return render_template("courses.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/users")
@login_required
def users():

    all_users = User.query.all()
    return render_template("users.html", users=all_users)

@app.route("/recommend", methods=["POST"])
@login_required
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
@login_required
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

@app.route("/admin")
@login_required
def admin():

    user = db.session.get(User, session["user_id"])

    if user.role != "admin":
        return "Access Denied", 403

    total_users = User.query.count()
    total_courses = Course.query.count()

    average_rating = round(
        db.session.query(db.func.avg(Course.rating)).scalar() or 0,
        1
    )

    return render_template(
        "admin.html",
        user=user,
        total_users=total_users,
        total_courses=total_courses,
        average_rating=average_rating
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)