import json

from mongoengine import signals
from email.utils import parseaddr
from application import db
from .transaction import FriendTransaction
from user.models.user import UserDB

class SocialDB(db.Document):
    """
    Class that maps to the database the friends list (users) of the user.
    
    Arguments:
        user -- The current user
        friends -- the list of users that accepted the requests made by the user
        friends_blocked -- the list of users the current user does not want to interact with
        friends_pending -- the list of transactions sent to users that the user requested to be in his list and is pending
        friends_request -- the list of transactions sent from users that requested the user to be in their contact list.
        friends_blocked_request -- the list of transactions sent to the system in order to block users (used to match the unblock transaction - it shall be removed then and moved to the general system transactions history).

    
    Reason: 
        The system itself will be treated as a social networking app for games evaluation.
        The set operations provided by the scsr is a differential to the other game analysis tools
    """
    user = db.ReferenceField(UserDB, db_field="user", primary_key=True)
    external_id = db.StringField(db_field="external_id", required=True, unique=True) #it is easier to maintain, a unique key other than the primary with the same name for all fields. (is it safe??)
    friends = db.ListField(db.ReferenceField(UserDB), db_field="friends")
    friends_blocked = db.ListField(db.ReferenceField(UserDB), db_field="friends_blocked")
    friends_pending = db.ListField(db.ReferenceField(FriendTransaction), db_field="friends_pending")
    friends_request = db.ListField(db.ReferenceField(FriendTransaction), db_field="friends_request")
    friends_blocked_request = db.ListField(db.ReferenceField(FriendTransaction), db_field="friends_blocked_request")

    def to_obj(self):
        retorno={
            "user": self.user.to_obj(),
            "friends": UserDB.to_obj_list(self.friends),
            "friends_blocked": UserDB.to_obj_list(self.friends_blocked),
            "friends_pending": FriendTransaction.to_obj_list(self.friends_pending),
            "friends_request": FriendTransaction.to_obj_list(self.friends_request),
            "friends_blocked_request": FriendTransaction.to_obj_list(self.friends_blocked_request),
            "links": [
                {"rel": "self", "href": "/social/" + self.user.external_id }
            ]

        }
        