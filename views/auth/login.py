from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
    g,
)
from werkzeug.security import check_password_hash
from database.models.user import User

login_route = Blueprint("login", __name__, url_prefix="/auth")


@login_route.route("/login", methods=("GET", "POST"))
def login():
    user_id = session.get("user_id")
    if user_id:
        return redirect(url_for("index"))
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        password = data.get("password")

        error = None

        if not email or not password:
            error = "email or password not provided"
        else:
            user = User.query.filter_by(email=email).first()

            if user is None:
                error = "Incorrect email."
            elif not check_password_hash(user.password, password):
                error = "Incorrect password."

            if error is None:
                session.clear()
                session["user_id"] = user.id
                return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")


@login_route.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()


@login_route.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("index"))
