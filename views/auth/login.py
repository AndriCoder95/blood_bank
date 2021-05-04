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

# needed for decoding password hashes. User class is needed too.
from werkzeug.security import check_password_hash
from database.models.user import User

# Blueprint for login route.
login_route = Blueprint("login", __name__, url_prefix="/auth")

# login page (prefix: /auth). Frontend is based on layout.html and login.html in templates folder
@login_route.route("/login", methods=("GET", "POST"))
def login():
    user_id = session.get("user_id")
    # Check if user is already logged in, redirect to home page if this is the case
    if user_id:
        return redirect(url_for("index"))
    # check if URL was visited with input from the form (login attempt)
    if request.method == "POST":
        # assign form input from login.html to variables
        data = request.form
        email = data.get("email")
        password = data.get("password")

        error = None

        # check if user exists and if password matches with the decoded password from database.
        if not email or not password:
            error = "email or password not provided"
        else:
            user = User.query.filter_by(email=email).first()

            if user is None:
                error = "Incorrect email."
            elif not check_password_hash(user.password, password):
                error = "Incorrect password."

            # if user is found in database and the password is correct: redirect to homepage and start a session
            if error is None:
                session.clear()
                session["user_id"] = user.id
                return redirect(url_for("index"))

        flash(error)
    # display login page when url is visited (without POST method from form)
    return render_template("auth/login.html")

# keep track of user information
@login_route.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()

# logout route, visited when logout button in navbar is clicked. session (cookies) get cleared.
@login_route.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("index"))
