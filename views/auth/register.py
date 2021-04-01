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
from werkzeug.security import generate_password_hash
from database.models.user import User, PrivacyEnum
from database import db

register_route = Blueprint("register", __name__, url_prefix="/auth")


@register_route.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("fullName")
        address = data.get("address")
        contact = data.get("contact")
        blood_type = data.get("bloodType")

        error = None

        if not email or not password:
            error = "Email or password not provided"

        else:
            try:
                hash_password = generate_password_hash(password)
                new_user = User(
                    email=email,
                    password=hash_password,
                    full_name=full_name,
                    address=address,
                    contact=contact,
                    blood_type=blood_type,
                )

                db.session.add(new_user)
                db.session.commit()

                return redirect(url_for("login.login"))
            except Exception as e:
                error = str(e)
        flash(error)

    user_id = session.get("user_id")
    if user_id:
        return redirect(url_for("index"))
    return render_template("auth/register.html")
