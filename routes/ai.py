from flask import Blueprint, render_template, request
from utils import login_required
from services.gemini_service import ask_ai

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/ai", methods=["GET", "POST"])
@login_required
def ai():

    answer = None

    if request.method == "POST":

        prompt = request.form["prompt"]

        answer = ask_ai(prompt)

    return render_template(
        "ai.html",
        answer=answer
    )