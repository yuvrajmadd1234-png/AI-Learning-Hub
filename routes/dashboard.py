from flask import Blueprint, render_template, session, redirect, url_for
from models import db, User, Course
from utils import login_required

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
@login_required
def dashboard():


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