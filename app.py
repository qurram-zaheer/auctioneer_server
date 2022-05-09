import json
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    unset_jwt_cookies, jwt_required, JWTManager

from Models.user import User
from custom_exceptions.email_exists import EmailAlreadyExistsException
from database_handler import DatabaseHandler
from werkzeug.security import generate_password_hash, check_password_hash

api = Flask(__name__)

api.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
jwt = JWTManager(api)

db_handler = DatabaseHandler()


@api.route('/register', methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    first_name = request.json.get("first_name", None)
    last_name = request.json.get("last_name", None)
    gender = request.json.get("gender", None)
    if email is None or password is None or first_name is None or last_name is None or gender is None:
        return {"msg": "Bad request"}, 400

    try:
        User(email, generate_password_hash(password), first_name, last_name, gender).create_user()
    except EmailAlreadyExistsException as ex:
        return {"msg": "Something went wrong", "error": ex.message}, 400

    access_token = create_access_token(identity=email)
    return {"msg": "success", "access_token": access_token}


@api.route('/login', methods=['POST'])
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email is None or password is None:
        return {"msg": "Bad request"}, 400

    try:
        user_record = User.get_user(email)
        if user_record and check_password_hash(user_record['password'], password):
            access_token = create_access_token(identity=email)
            return {"msg": "success", "access_token": access_token}

        return {"msg": "Authentication failed! Please create an account or check your email and password"}, 401

    except Exception as ex:
        return {"msg": "Something went wrong", "error": str(ex)}, 400


if __name__ == '__main__':
    api.run()
