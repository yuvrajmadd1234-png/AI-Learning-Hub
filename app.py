from flask import Flask, render_template
from flask_migrate import Migrate
from models import db, User, Course
from routes.dashboard import dashboard_bp
from routes.auth import auth
from utils import login_required
from routes.courses import courses_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from routes.recommendation import recommendation_bp
from routes.ai import ai_bp
import os

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(auth)

app.register_blueprint(dashboard_bp)

app.register_blueprint(courses_bp)

app.register_blueprint(profile_bp)

app.register_blueprint(admin_bp)

app.register_blueprint(recommendation_bp)

app.register_blueprint(ai_bp)

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

@app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("errors/500.html"), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)