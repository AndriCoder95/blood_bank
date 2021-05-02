# Import the necessary libraries, classes & helper functions from other files
from flask import Flask, render_template, session, redirect, url_for, g, request, flash
from views.auth.login import login_route
from views.auth.register import register_route
from views.notification.notification import notification_route
from database import db
from database.models.user import User, PrivacyEnum
from database.models.notifications import Notification, NotificationEnum
from sqlalchemy.sql.expression import func, select
from helper import blood_group_change, privacy_helper, blood_group_change_reverse
from sys import platform

# Create an instance of class Flask
app = Flask(__name__)

# Make sure database queries work on different operating systems (db file stored in a temporary folder)
if platform == "win32" or platform == "cygwin":
    app.config["SQLALCHEMY_DATABASE_URI"] = r'sqlite:///C:\temp\g.db'
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/g.db"
db.init_app(app)

# registering blueprint
app.register_blueprint(login_route)
app.register_blueprint(register_route)
app.register_blueprint(notification_route)

app.secret_key = "SECRET_KEY"

# starting page. Frontend is based on layout.html and index.html in the template folder
@app.route("/", methods=["GET", "POST"])
def index():
    user_id = session.get("user_id")
    # check if user is logged in, otherwise redirect to login page (leveraging the blueprint)
    if user_id is None:
        return redirect(url_for("login.login"))

    if request.method == "POST":
        try:
            requesting_user = g.user
            requested_user_email = request.form.get("requested_user")
            requested_user = User.query.filter_by(email=requested_user_email).first()
            if not requested_user:
                flash("Invalid user")
            else:
                notification = Notification(
                    requesting_user=requesting_user, requested_to=requested_user
                )
                db.session.add(notification)
                db.session.commit()

        except Exception as e:
            flash(str(e))

    queries = request.args
    blood_type_old = queries.get("bloodType")
    address = queries.get("address")

    random_donors = User.query.order_by(func.random()).filter(User.id != user_id)

    if blood_type_old:
        blood_type = blood_group_change_reverse(blood_type_old)
        random_donors = random_donors.filter(User.blood_type == blood_type)

    if address:
        random_donors = random_donors.filter(
            func.lower(User.address) == func.lower(address)
        )

    random_donors = random_donors.limit(10)

    donors = []
    for donor in random_donors:
        donor_dict = {}
        donor_dict["blood_type"] = blood_group_change(donor.blood_type)
        donor_dict["full_name"] = donor.full_name
        donor_dict["email"] = donor.email
        privacy_state = privacy_helper(donor.privacy)
        donor_dict["privacy"] = privacy_state
        if privacy_state == "public":
            donor_dict["address"] = donor.address
            donor_dict["contact"] = donor.contact
        else:

            notification = Notification.query.filter_by(
                requesting_user_id=g.user.id, requested_to_id=donor.id
            ).first()
            if notification:
                if notification.status == NotificationEnum.pending:
                    donor_dict["address"] = "Confidential"
                    donor_dict["contact"] = "Pending Request"
                elif notification.status == NotificationEnum.accepted:
                    donor_dict["address"] = donor.address
                    donor_dict["contact"] = donor.contact
            else:
                donor_dict["address"] = "Confidential"
                donor_dict["contact"] = "Request Information"

        donors.append(donor_dict)

    if not address:
        address = ""
    selected_values = {"blood_type": blood_type_old, "address": address}
    return render_template(
        "blood/index.html", user=g.user, donors=donors, selected_values=selected_values
    )


@app.route("/account", methods=["GET", "POST"])
def account():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login.login"))

    if request.method == "POST":
        data = request.form
        user = User.query.filter_by(id=user_id).first()

        try:
            user.email = data.get("email")
            user.full_name = data.get("fullName")
            user.address = data.get("address")
            user.contact = data.get("contact")
            user.blood_type = data.get("bloodType")
            user.privacy = (
                PrivacyEnum.private
                if data.get("privacy") == "private"
                else PrivacyEnum.public
            )

            db.session.commit()
        except Exception as e:
            flash(str(e))

        g.user = user

    return render_template("blood/accounts.html", user=g.user)


if __name__ == "__main__":
    from database.models.user import User
    from database.models.notifications import Notification

    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
