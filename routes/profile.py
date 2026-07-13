from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User
from utils import login_required

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
@login_required
def profile():

    user = db.session.get(User, session["user_id"])

    return render_template(
        "profile.html",
        user=user
    )

@profile_bp.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]

        db.session.commit()

        return redirect(url_for("profile.profile"))

    return render_template(
        "edit_profile.html",
        user=user
    )