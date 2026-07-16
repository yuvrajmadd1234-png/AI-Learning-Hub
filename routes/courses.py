from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Course
from utils import login_required

courses_bp = Blueprint("courses", __name__)

@courses_bp.route("/courses")
@login_required
def courses():

    page = request.args.get("page", 1, type=int)

    courses = Course.query.paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    return render_template(
        "courses.html",
        courses=courses
    )

@courses_bp.route("/add_course", methods=["GET", "POST"])
@login_required
def add_course():

    user = db.session.get(User, session["user_id"])

    if user.role != "admin":
        return "Access Denied", 403

    if request.method == "POST":

        course_name = request.form["name"]
        category = request.form["category"]
        rating = float(request.form["rating"])
        level = request.form["level"]

        new_course = Course(
            course=course_name,
            category=category,
            description="No description available.",
            duration="Self-paced",
            level=level,
            rating=rating
        )

        db.session.add(new_course)
        db.session.commit()

        flash("Course added successfully!", "success")

        return redirect(url_for("courses.courses"))
    return render_template("add_course.html")

@courses_bp.route("/delete_course/<int:id>")
@login_required
def delete_course(id):

    user = db.session.get(User, session["user_id"])

    if user.role != "admin":
        return "Access Denied", 403

    course = Course.query.get_or_404(id)

    db.session.delete(course)
    db.session.commit()

    flash("Course deleted successfully!", "success")

    return redirect(url_for("courses.courses"))

@courses_bp.route("/edit_course/<int:id>", methods=["GET", "POST"])
@login_required
def edit_course(id):

    user = db.session.get(User, session["user_id"])

    if user.role != "admin":
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for("dashboard.dashboard"))

    course = Course.query.get_or_404(id)

    if request.method == "POST":

        course.course = request.form["name"]
        course.category = request.form["category"]
        course.level = request.form["level"]
        course.rating = float(request.form["rating"])

        db.session.commit()

        flash("Course updated successfully!", "success")

        return redirect(url_for("courses.courses"))

    return render_template(
        "edit_course.html",
        course=course
    )