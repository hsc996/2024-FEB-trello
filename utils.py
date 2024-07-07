from flask_jwt_extended import get_jwt_identity
from init import db
from models.user import User


def authorise_as_admin():
    # Get the users id from jwt identity
    user_id = get_jwt_identity()
    # fetch the user from the db
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    # check whether the user is an admin or not
    return user.is_admin