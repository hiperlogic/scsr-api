from flask.views import MethodView
from flask import jsonify, request, abort, render_template
import uuid
import json
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
from datetime import datetime

from sys_app.decorators import app_required
from user.models.user import UserDB


class UserAPI(MethodView):
    """
    API class for user manipulation - Retrieval, Storage, Update and (Logical) Delete

    Attributes:
        DATA_PER_PAGE: Pagination quantification parameter
        decorators: decorators applied to each one of the methods

    Methods:
    ================================
    Name: __init__
    Parameters: None
    Role: Constructor
    Result: Setup DATA_PER_PAGE and provides basic validation regarding data states
    Requirements: None
    ================================
    Name: get
    Parameters: user_id (optional)
    Role: Data Retrieval
    Result: Return all users or one specific user if requested - or access denied
    Requirements: Authentication
    ================================
    Name: post
    Parameters: None
    Role: Creates and stores user data on the database
    Result: Returns the user stored - or access denied
    Requirements: Authentication
    ================================
    Name: Put
    Parameters: user_id
    Role: Data modification
    Result: Return the data in the modified state
    Requirements: Authentication
    ================================
    Name: Delete
    Parameters: user_id
    Role: Data modification - logical deletion
    Result: Confirmation of deletion
    Requirements: Authentication
    """

    decorators = [app_required]

    def __init__(self):
        self.DATA_PER_PAGE=10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self, user_id):
        if user_id:
            user = User.objects.filter(external_id=user_id, live=True).first()
            if user:
                response = {
                    "result": "ok",
                    "user": user_obj(user)
                }
                return jsonify(response), 200
            else:
                return jsonify({}), 404
        else:
            users = UserDB.objects.filter(live=True)
            page = int(request.args.get('page',1))
            users = users.paginate(page=page, per_page = self.DATA_PER_PAGE)
            response = {
                "result": "ok",
                "links": [
                    {
                        "href": "/users/?page=%s" % page,
                        "rel": "self"
                    }
                ],
                "users": UserDB.users_obj(users)
            }
            if users.has_prev:
                response["links"].append(
                    {
                        "href": "/users/?page=%s" % (users.prev_num),
                        "rel": "previous"
                    }
                )
            if users.has_next:
                response["links"].append(
                    {
                        "href": "/users/?page=%s" % (users.next_num),
                        "rel": "next"
                    }
                )
            return jsonify(response), 200

    def post(self):
        user_json = request.json
        error = best_match(Draft4Validator(UserDB.getSchema()).iter_errors(user_json))
        if error:
            return jsonify({"error": error.message}), 400
        else:
            user = User(
                external_id=str(uuid.uuid4()),
                country = user_json.get("country"),
                state = user_json.get("state"),
                city = user_json.get("city"),
                lang = user_json.get("lang"),
                name = user_json.get("name"),
                surname = user_json.get("surname"),
                username = user_json.get("username"),
                email = user_json.get("email"),
                password = user_json.get("password"),
                bio = user_json.ger("bio"),
                live = True,
                created = datetime.utcnow()
            ).save()
            response = {
                "result": "ok",
                "user": user_obj(user)
            }
            return jsonify(response), 201

    def put(self, user_id):
        user = UserDB.objects.filter(external_id=user_id, live=True).first()
        if not user:
            return jsonify({}), 404
        user_json = request.json
        error = best_match(Draft4Validator(UserDB.getSchema()).iter_errors(user_json))
        if error:
            return jsonify({"error": error.message}), 400
        else:
            user.country = user_json.get("country")
            user.state = user_json.get("state")
            user.city = user_json.get("city")
            user.name = user_json.get("name")
            user.surname = user_json.get("surname")
            user.username = user_json.get("username")
            user.email = user_json.get("email")
            user.password = user_json.get("password")
            user.save()
            response = {
                "result": "ok",
                "user": user.get_object()
            }
            return jsonify(response), 200

    def delete(self, user_id):
        user = User.objects.filter(external_id=user_id, live=True).first()
        if not user:
            return jsonify({}), 404
        user.live = False
        user.save()
        return jsonify({}), 204
        