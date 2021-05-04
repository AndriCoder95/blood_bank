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

# import of classes that will store our data and build the structure for our database.
from database.models.notifications import Notification, NotificationEnum
from database.models.user import User
from database import db
from helper import blood_group_change

#Blueprint for notification route.
notification_route = Blueprint("notification", __name__, url_prefix="/notification")

# notification page (see prefix of blueprint). Frontend based on layout.html and notification.html in templates folder
@notification_route.route("/", methods=["GET", "POST"])
def notification():
    user_id = session.get("user_id")
    # check if user is logged in otherwise redirect the user to the login page.
    if user_id is None:
        return redirect(url_for("login.login"))
    # check if form in notifications.html was submitted (in case that the user had outstanding requests)
    if request.method == "POST":
        # change notification status in database.
        data = request.form
        request_id = data.get("request_id")
        try:
            notification = Notification.query.filter_by(id=request_id).first()
            notification.status = NotificationEnum.accepted
            db.session.commit()
        except Exception as e:
            flash(str(e))
    # collect all requests raised by the user that were accepted by other donors.
    accepted_requests_list = Notification.query.filter_by(
        requesting_user_id=g.user.id, status=NotificationEnum.accepted
    )
    # bring the accepted requests in another format before sending them to the client for displaying
    accepted_requests = []
    for accepted_request in accepted_requests_list:
        item = {}
        item["created_at"] = accepted_request.created_at
        item["requested_to"] = User.query.filter_by(
            id=accepted_request.requested_to_id
        ).first()
        item["blood_type"] = blood_group_change(item["requested_to"].blood_type)
        accepted_requests.append(item)
    # update the list of incoming requests (which are displayed too in notifications.html)
    incoming_requests_list = Notification.query.filter_by(
        requested_to_id=g.user.id, status=NotificationEnum.pending
    )
    # bring the incoming requests in another format before sending them to the client for displaying
    incoming_requests = []
    for incoming_request in incoming_requests_list:
        item = {}
        item["created_at"] = incoming_request.created_at
        item["requesting_user"] = User.query.filter_by(
            id=incoming_request.requesting_user_id
        ).first()
        item["id"] = incoming_request.id

        incoming_requests.append(item)
    # Send notifications.html to the client with parameters according to user related data.
    # Determines what will be displayed in browser.
    return render_template(
        "blood/notifications.html",
        user=g.user,
        accepted_requests=accepted_requests,
        incoming_requests=incoming_requests,
    )
