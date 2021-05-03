from database.models.user import BloodGroupEnum, PrivacyEnum

# Helper Functions

def blood_group_change(blood_enum):
    if blood_enum == BloodGroupEnum.a_negative:
        return "A-"
    if blood_enum == BloodGroupEnum.a_positive:
        return "A+"
    if blood_enum == BloodGroupEnum.ab_negative:
        return "AB-"
    if blood_enum == BloodGroupEnum.ab_positive:
        return "AB+"
    if blood_enum == BloodGroupEnum.b_negative:
        return "B-"
    if blood_enum == BloodGroupEnum.b_positive:
        return "B+"
    return "Unknown"


def blood_group_change_reverse(blood_group):
    if blood_group == "A-":
        return BloodGroupEnum.a_negative
    if blood_group == "A+":
        return BloodGroupEnum.a_positive
    if blood_group == "AB-":
        return BloodGroupEnum.ab_negative
    if blood_group == "AB+":
        return BloodGroupEnum.ab_positive
    if blood_group == "B-":
        return BloodGroupEnum.b_negative
    if blood_group == "B+":
        return BloodGroupEnum.b_positive

# Helps determining the privacy setting of a user
def privacy_helper(privacy):
    if privacy == PrivacyEnum.public:
        return "public"
    return "private"
