from flask import Blueprint, request, jsonify
from .models import db, User
import jwt
import datetime
from functools import wraps

auth_bp = Blueprint('auth', __name__)

SECRET = "YOUR_SECRET_KEY"  # change later

# Generate Token
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"msg": "Token missing"}), 401

        try:
            data = jwt.decode(token.split(" ")[1], SECRET, algorithms=["HS256"])
        except:
            return jsonify({"msg": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorator


# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data["name"]
    email = data["email"]
    password = data["password"]

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Registration successful"})


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 400

    token = jwt.encode(
        {"id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)},
        SECRET,
        algorithm="HS256"
    )

    return jsonify({"token": token})
