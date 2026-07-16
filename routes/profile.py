from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, User
from utils import login_required
from flask import flash

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
@login_required
def edit_profile():


    user = db.session.get(User, session["user_id"])

    if request.method == "POST":

        user.name = request.form["name"]
        user.email = request.form["email"]

        db.session.commit()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("profile.profile"))

    return render_template(
        "edit_profile.html",
        user=user
    )