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

from database.models.notifications import Notification, NotificationEnum
from database.models.user import User
from database import db
from helper import blood_group_change

notification_route = Blueprint("notification", __name__, url_prefix="/notification")


@notification_route.route("/", methods=["GET", "POST"])
def notification():
    user_id = session.get("user_id")
    if user_id is None:
        return redirect(url_for("login.login"))

    if request.method == "POST":

        data = request.form
        request_id = data.get("request_id")
        try:
            notification = Notification.query.filter_by(id=request_id).first()
            notification.status = NotificationEnum.accepted
            db.session.commit()
        except Exception as e:
            flash(str(e))

    accepted_requests_list = Notification.query.filter_by(
        requesting_user_id=g.user.id, status=NotificationEnum.accepted
    )

    accepted_requests = []
    for accepted_request in accepted_requests_list:
        item = {}
        item["created_at"] = accepted_request.created_at
        item["requested_to"] = User.query.filter_by(
            id=accepted_request.requested_to_id
        ).first()
        item["blood_type"] = blood_group_change(item["requested_to"].blood_type)
        accepted_requests.append(item)

    incoming_requests_list = Notification.query.filter_by(
        requested_to_id=g.user.id, status=NotificationEnum.pending
    )

    incoming_requests = []
    for incoming_request in incoming_requests_list:
        item = {}
        item["created_at"] = incoming_request.created_at
        item["requesting_user"] = User.query.filter_by(
            id=incoming_request.requesting_user_id
        ).first()
        item["id"] = incoming_request.id

        incoming_requests.append(item)

    return render_template(
        "blood/notifications.html",
        user=g.user,
        accepted_requests=accepted_requests,
        incoming_requests=incoming_requests,
    )
