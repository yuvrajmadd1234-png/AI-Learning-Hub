from flask import Blueprint, redirect, render_template, request, url_for
from models import db, Course
from utils import login_required
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

recommendation_bp = Blueprint("recommendation", __name__)

@recommendation_bp.route("/recommend", methods=["POST"])
@login_required
def recommend():
    interest = request.form.get("interest")

    if not interest:
        return redirect(url_for("dashboard.dashboard"))

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

@recommendation_bp.route("/search", methods=["POST"])
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

@recommendation_bp.route("/import")
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
