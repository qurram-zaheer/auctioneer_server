import json
import os

from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    unset_jwt_cookies, jwt_required, JWTManager, create_refresh_token, set_refresh_cookies
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from Models.listing import Listing
from Models.user import User
from custom_exceptions.email_exists import EmailAlreadyExistsException
from database_handler import DatabaseHandler
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

api = Flask(__name__)
cors = CORS(api, supports_credentials=True)
api.config['CORS_HEADERS'] = 'Content-Type'
api.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
jwt = JWTManager(api)

db_handler = DatabaseHandler()
BID_EXPIRY_TIME = 1


@api.route('/register', methods=["POST"])
@cross_origin()
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    first_name = request.json.get("firstName", None)
    last_name = request.json.get("lastName", None)
    gender = request.json.get("gender", None)
    if email is None or password is None or first_name is None or last_name is None or gender is None:
        return {"msg": "Bad request"}, 400

    try:
        uid = User(email, generate_password_hash(password), first_name, last_name, gender).create_user()
    except EmailAlreadyExistsException as ex:
        return {"msg": "Something went wrong", "error": ex.message}, 400

    access_token = create_access_token(identity=email)
    resp = jsonify({"msg": "success", "access_token": access_token, "user": uid})
    return resp, 200


@api.route('/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email is None or password is None:
        return {"msg": "Bad request"}, 400

    try:
        user_record = User.get_user(email)
        if user_record and check_password_hash(user_record['password'], password):
            access_token = create_access_token(identity=email)
            resp = jsonify({"msg": "success", "access_token": access_token, "user": str(user_record["_id"])})
            return resp, 200

        return {"msg": "Authentication failed! Please create an account or check your email and password"}, 401

    except Exception as ex:
        return {"msg": "Something went wrong", "error": str(ex)}, 400


@api.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200




@api.route("/listing", methods=["POST", "GET"])
@cross_origin()
def listing_route():
    if request.method == 'POST':
        try:
            doc = request.json
            name = doc.get('name')
            subtitle = doc.get('subtitle')
            cost = doc.get('cost')
            desc = doc.get('desc')
            features = doc.get('features')
            specs = doc.get('specs')
            max_cost = doc.get('max_cost')
            image = doc.get('image')
            print(doc)
            _id = Listing(name=name, specs=specs, features=features, cost=cost, desc=desc, subtitle=subtitle,
                          max_cost=max_cost, image=image).create_listing()
            print(_id)
            rec = Listing.get_listing(_id)
            print(rec)
            return {"msg": "Success"}, 200
        except Exception as ex:
            return {"msg": "Something went wrong", "error": str(ex)}, 400
    elif request.method == "GET":
        doc_id = request.args.get("id")
        record = Listing.get_listing(doc_id)
        current_ts = datetime.now()
        stored_ts = datetime.fromtimestamp(record['timestamp'])
        td = (current_ts - stored_ts).days * 24 * 60 + (current_ts - stored_ts).seconds / 60

        if td >= BID_EXPIRY_TIME and len(record['bids']) > 0:
            print("IN HERE LOL")
            Listing.sell_listing(record["bids"][-1]['user'], doc_id)

        record = Listing.get_listing(doc_id)
        print(record)
        return {"msg": "success", "listing": record}, 200


@api.route("/listings", methods=["GET"])
def all_listings():
    try:
        listings = Listing.get_all_listings()
        return {"msg": "success", "listings": listings}, 200
    except Exception as ex:
        return {"msg": "Something went wrong", "error": str(ex)}, 400


@api.route("/bid", methods=["POST"])
@cross_origin()
def make_bid():
    # try:
    listing_id = request.json['id']
    bid = request.json['bid']
    email = bid['user']
    user_id = str(User.get_user(email)["_id"])
    bid['user'] = user_id
    ack = Listing.add_bid(listing_id, request.json["bid"])
    return {"msg": "success", "ack": ack}


@api.route("/user/listings", methods=["GET"])
@cross_origin()
def get_listings_for_user():
    user_email = request.args.get("email")
    user = User.get_user(user_email)
    user_id = str(user["_id"])
    listings_for_user = Listing.get_user_listings(user_id)
    return {"msg": "success", "listings": listings_for_user}, 200
