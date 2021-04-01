from database import db
import enum


class BloodGroupEnum(enum.Enum):
    a_positive = "A+"
    a_negative = "A-"
    b_positive = "B+"
    b_negative = "B-"
    o_positive = "B+"
    o_negative = "B-"
    ab_positive = "AB+"
    ab_negative = "AB-"


class PrivacyEnum(enum.Enum):
    public = "public"
    private = "private"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(32), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    blood_type = db.Column(db.Enum(BloodGroupEnum), nullable=False)
    privacy = db.Column(db.Enum(PrivacyEnum), default=PrivacyEnum.public)