from datetime import timedelta

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError
from psycopg2 import errorcodes
from flask_jwt_extended import create_access_token

from init import bcrypt, db
from models.user import User, user_schema


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("register", methods=["POST"])
def register_user():
    try:
        # Get the data from the body of the request
        body_data = request.get_json()

        # Create an instance of the user model
        user = User(
            name=body_data.get("name"),
            email=body_data.get("email")
        )

        # Hash the password
        password = body_data.get("password")
        if password:
            user.password = bcrypt.generate_password_hash(password).decode("utf-8")

        # Add and commit and the database
        db.session.add(user)
        db.session.commit()

        # Response back to the client
        return user_schema.dump(user), 201
    
    except IntegrityError as err:
        # not null violation
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"error": f"The column {err.orig.diag.column_nameq} required"}, 409
            # unique violation
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"error": "Email address already in use"}, 409


@auth_bp.route("/login", methods=["POST"])
def login_user():
    # Get the data from the body of the request
    body_data = request.get_json()

    # Find the user in the DB with that email address
    stmt = db.select(User).filter_by(email=body_data.get("email"))
    user = db.session.scalar(stmt)

    # If user exists and password is correct
    if user and bcrypt.check_password_hash(user.password, body_data.get("password")):
        # Create JWT
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        # Repond back to the user
        return {"email": user.email, "is_admin": user.is_admin, "token": token}
    # Else
    else:
        # Rspond with error message
        return {"error": "Invalid email or password"}, 401



