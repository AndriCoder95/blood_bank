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
# libraries needed to encode password information
from werkzeug.security import generate_password_hash
from database.models.user import User, PrivacyEnum
from database import db

# Blueprint for register route
register_route = Blueprint("register", __name__, url_prefix="/auth")

# register page (prefix: /auth). Frontend is based on layout.html and register.html in templates folder
@register_route.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        # get user input from the form in register.html
        data = request.form
        email = data.get("email")
        password = data.get("password")
        full_name = data.get("fullName")
        address = data.get("address")
        contact = data.get("contact")
        blood_type = data.get("bloodType")

        error = None

        # most important variables, however frontend checks already for all variables to be given correctly.
        if not email or not password:
            error = "Email or password not provided"

        else:
            try:
                # encode password
                hash_password = generate_password_hash(password)
                # create a new user and add to the database
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

                # redirect user to login page after successful registration
                return redirect(url_for("login.login"))
            except Exception as e:
                error = str(e)
        flash(error)

    # redirect user to home page if logged in or display register.html if the url is visited without POST from form
    user_id = session.get("user_id")
    if user_id:
        return redirect(url_for("index"))
    return render_template("auth/register.html")
