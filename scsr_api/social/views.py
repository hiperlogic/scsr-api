from flask import Blueprint
from social.api import SocialAPI


social_app = Blueprint("social_app", __name__)

social_view = SocialAPI.as_view("social_api")

"""GET Method: Returns the data for the user ID IF the user requested is authorized and an admin or the user itself
"""

social_app.add_url_rule('/social/',defaults={"user_id":None}, 
    view_func=social_view, methods=['GET',])

"""POST method
    Pushes a new transaction into the system.
    The post may be:
    - a Request transaction: creates a new transaction on friend request.
    - a Cancel transaction: cancels the friendship relation - creates an Automatic accepted transaction
    - a Block transaction: freezes the communication between the relation - creates and Automatic accepted transaction
    - an Unblock transaction: unfreezes the communication between the relation - creates an Automatic accepeted transaction mapped with the corresponding block transaction

"""

social_app.add_url_rule("/social/", view_func=social_view, methods=['POST',])

"""GET, PUT, DELETE
    Updates the transaction related to the User provided in the user ID IF the user requested is authorized and is the same or an admin.
    The update may be:
    - a Reject for a requested transaction (no new transaction made) (in the delete) or 
    - an Accept for a requested transaction (no new transaction made) (in the put)

"""

social_app.add_url_rule("/social/<user_id>", view_func=social_view, methods=['GET', "PUT", "DELETE",])
