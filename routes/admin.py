from flask import Blueprint, render_template, session, Response
from models import db, User, Course
from utils import login_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
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

    latest_users = User.query.order_by(User.id.desc()).limit(5).all()
    latest_courses = Course.query.order_by(Course.id.desc()).limit(5).all()

    total_categories = db.session.query(
    Course.category
    ).distinct().count()

    return render_template(
        "admin/dashboard.html",
        user=user,
        total_users=total_users,
        total_courses=total_courses,
        average_rating=average_rating,
        latest_users=latest_users,
        latest_courses=latest_courses,
        total_categories=total_categories
    )

@admin_bp.route("/users")
@login_required
def users():

    user = db.session.get(User, session["user_id"])

    if user.role != "admin":
        return "Access Denied", 403

    all_users = User.query.all()

    return render_template(
        "admin/users.html",
        users=all_users
    )

@admin_bp.route("/analytics")
@login_required
def analytics():

    user = db.session.get(User, session["user_id"])

    if user.role != "admin":
        return "Access Denied", 403

    total_users = User.query.count()
    total_courses = Course.query.count()

    total_categories = db.session.query(
        Course.category
    ).distinct().count()

    return render_template(
        "admin/analytics.html",
        user=user,
        total_users=total_users,
        total_courses=total_courses,
        total_categories=total_categories
    )

@admin_bp.route("/export-users")
@login_required
def export_users():

    user = db.session.get(User, session["user_id"])

    if user.role != "admin":
        return "Access Denied", 403

    users = User.query.all()

    csv = "ID,Name,Email,Role\n"

    for u in users:
        csv += f"{u.id},{u.name},{u.email},{u.role}\n"

    return Response(
        csv,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=users.csv"
        }
    )

@admin_bp.route("/export-courses")
@login_required
def export_courses():

    user = db.session.get(User, session["user_id"])

    if user.role != "admin":
        return "Access Denied", 403

    courses = Course.query.all()

    csv = "ID,Course,Category,Level,Rating\n"

    for c in courses:
        csv += f"{c.id},{c.course},{c.category},{c.level},{c.rating}\n"

    return Response(
        csv,
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=courses.csv"
        }
    )