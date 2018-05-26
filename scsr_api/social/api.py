from flask.views import MethodView
from flask import jsonify, request, abort, render_template
import uuid
import json
from jsonschema import Draft4Validator
from jsonschema.exceptions import best_match
from app.decorators import app_required
from social.models import FriendTransaction, Social
from user.templates import user_obj, users_obj
from social.templates import social_obj
from user.models import User

class SocialAPI(MethodView):
    """
    API class for social manipulation - Retrieval, Storage, Update and (Logical) Delete

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
    Requirements: Authentication, the user must have access to the requested data
    ================================
    Name: post
    Parameters: None
    Role: Creates and stores user data on the database
    Result: Returns the user stored - or access denied
    Requirements: Authentication, the user must have access to the requested feature
    ================================
    Name: Put
    Parameters: user_id
    Role: Data modification
    Result: Return the data in the modified state
    Requirements: Authentication, the user must have access to the requested feature
    ================================
    Name: Delete
    Parameters: user_id
    Role: Data modification - logical deletion
    Result: Confirmation of deletion
    Requirements: Authentication, the user must have access to the requested feature
    """
    decorators = [app_required]

    def __init__(self):
        """ 
            Constructor

            No parameters
        """

        self.DATA_PER_PAGE=10
        if (request.method != 'GET' and request.method != 'DELETE') and not request.json:
            abort(400)

    def get(self, user_id):
        """ Called for Get Method
        
        Arguments:
            user_id - Identification to get the user friends data and transactions
        
        Returns:
            User friends data and pending transactions

        Requires: Authentication, Same ID from User ID in Auth
        """

        if user_id:
            social = Social.objects.filter(user=user_id, live=True).first()
            if user:
                response = {
                    "result": "ok",
                    "user": user_obj(user)
                }
                return jsonify(response), 200
            else:
                return jsonify({}), 404
        else:
            users = User.objects.filter(live=True)
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
                "users": users_obj(users)
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
        error = best_match(Draft4Validator(UserSchema.schema).iter_errors(user_json))
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
                e_mail = user_json.get("e_mail"),
                password = user_json.get("password"),

            ).save()
            response = {
                "result": "ok",
                "user": user_obj(user)
            }
            return jsonify(response), 201

    def put(self, user_id):
        user = User.objects.filter(external_id=user_id, live=True).first()
        if not user:
            return jsonify({}), 404
        user_json = request.json
        error = best_match(Draft4Validator(UserSchema.schema).iter_errors(user_json))
        if error:
            return jsonify({"error": error.message}), 400
        else:
            user.country = user_json.get("country")
            user.state = user_json.get("state")
            user.city = user_json.get("city")
            user.name = user_json.get("name")
            user.surname = user_json.get("surname")
            user.username = user_json.get("username")
            user.e_mail = user_json.get("e_mail")
            user.password = user_json.get("password")
            user.save()
            response = {
                "result": "ok",
                "user": user_obj(user)
            }
            return jsonify(response), 200

    def delete(self, user_id):
        user = User.objects.filter(external_id=user_id, live=True).first()
        if not user:
            return jsonify({}), 404
        user.live = False
        user.save()
        return jsonify({}), 204
