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

    # enable the user to request information of another donor if this other donor is in private mode
    # Sends a notification to the other donor, his email is returned as requested user from the client
    if request.method == "POST":
        try:
            requesting_user = g.user
            requested_user_email = request.form.get("requested_user")
            requested_user = User.query.filter_by(email=requested_user_email).first()
            if not requested_user:
                flash("Invalid user")
            # request the donor for his private information (request needs to be stored in database)
            else:
                notification = Notification(
                    requesting_user=requesting_user, requested_to=requested_user
                )
                db.session.add(notification)
                db.session.commit()

        except Exception as e:
            flash(str(e))

    # Get the URL parameters bloodType and address
    queries = request.args
    blood_type_old = queries.get("bloodType")
    address = queries.get("address")

    # Get random donors (exclude the own user id)
    random_donors = User.query.order_by(func.random()).filter(User.id != user_id)

    # Filter the list of random donors according to the user input, i.e. if he looks for a particular address or blood type
    if blood_type_old:
        blood_type = blood_group_change_reverse(blood_type_old)
        random_donors = random_donors.filter(User.blood_type == blood_type)

    if address:
        random_donors = random_donors.filter(
            func.lower(User.address) == func.lower(address)
        )

    # Limit the number of donors displayed on the homepage to 10 (due to privacy reasons)
    random_donors = random_donors.limit(10)

    donors = []

    # Go through the max. 10 random donors and decide which information to display to the user
    for donor in random_donors:
        donor_dict = {}
        donor_dict["blood_type"] = blood_group_change(donor.blood_type)
        donor_dict["full_name"] = donor.full_name
        donor_dict["email"] = donor.email
        privacy_state = privacy_helper(donor.privacy)
        donor_dict["privacy"] = privacy_state
        # Handle the case where the displayed donors chose a public disclosure of their information
        if privacy_state == "public":
            donor_dict["address"] = donor.address
            donor_dict["contact"] = donor.contact

        # Handle cases where the displayed donors chose a private disclosure of their information
        else:
            notification = Notification.query.filter_by(
                requesting_user_id=g.user.id, requested_to_id=donor.id
            ).first()
            # Handle the case where the user has already requested information from the donor
            if notification:
                # Case where the donor did not yet respond to the users request
                if notification.status == NotificationEnum.pending:
                    donor_dict["address"] = "Confidential"
                    donor_dict["contact"] = "Pending Request"
                # case where the donor accepted the user request: display address and contact information
                elif notification.status == NotificationEnum.accepted:
                    donor_dict["address"] = donor.address
                    donor_dict["contact"] = donor.contact
            # Handle the case where the user did not yet ask the donor for displaying his contact details
            else:
                donor_dict["address"] = "Confidential"
                donor_dict["contact"] = "Request Information"

        donors.append(donor_dict)

    # No value (empty string) in html form if the user this not search for a specific location
    if not address:
        address = ""
    # Keep track of selected user input
    selected_values = {"blood_type": blood_type_old, "address": address}
    # return HTML template for home page when visiting URL: .../. Adjusted according to specific user input
    return render_template(
        "blood/index.html", user=g.user, donors=donors, selected_values=selected_values
    )

# Account page. Frontend is based on layout.html and index.html in the templates folder
# Reach this page by clicking on account in navbar
@app.route("/account", methods=["GET", "POST"])
def account():
    user_id = session.get("user_id")
    # check if user is logged in, otherwise redirect to the login page
    if user_id is None:
        return redirect(url_for("login.login"))

    # form submissions in accounts.html are sent by post method.
    if request.method == "POST":
        data = request.form
        user = User.query.filter_by(id=user_id).first()

        # adjust user information in database
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

    # Display HTML template for the account url with the specific user information & input adaptions
    return render_template("blood/accounts.html", user=g.user)

### Note that other routes (login, register, notification) were outsourced as python files to the views folder!

# Run the app (here in debug mode)
if __name__ == "__main__":
    from database.models.user import User
    from database.models.notifications import Notification

    # create temporary database in tmp folder
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
