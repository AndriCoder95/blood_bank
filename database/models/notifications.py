from database import db
import datetime
from database.models.user import User, BloodGroupEnum
import enum

# Notification status
class NotificationEnum(enum.Enum):
    accepted = "accepted"
    pending = "pending"

# Notifications to request donor information
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    requesting_user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    requested_to_id = db.Column(db.Integer, db.ForeignKey(User.id))
    requesting_user = db.relationship(
        "User",
        foreign_keys="Notification.requesting_user_id",
    )
    requested_to = db.relationship("User", foreign_keys="Notification.requested_to_id")
    status = db.Column(db.Enum(NotificationEnum), default=NotificationEnum.pending)
