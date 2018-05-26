import json

from mongoengine import signals
from email.utils import parseaddr
from application import db

class FriendTransaction(db.Document):
    """
    Class that represents a friend request/cancelation/block transaction
    Attributes:
        type: The type of transaction - [REQUEST, CANCEL, BLOCK, UNBLOCK]
        dateRequest: The date the transaction was made
        sender: Who issued the request
        receiver: To whom the request was issued
        status: What is the status of the transaction: Accepted, Rejected, Pending
    Reasons:
        Maintaining the transactions for friend request allows for the administrators to perform governance tasks.
    """

    """Transaction Type:
        Refers to what the transaction means.
        The CNL and BLK transaction types must refer to a REQ transaction
        The UBL transaction type must refer to a BLK transaction
    """

    type = {
        "REQ": "REQUEST",
        "CNL": "CANCEL",
        "BLK": "BLOCK",
        "UBL": "UNBLOCK"
    }

    
    status_codes = {
        "PND": "PENDING",
        "ACC": "ACCEPTED",
        "REJ": "REJECTED"
    }

    external_id = db.StringField(db_field="external_id", required=True)
    date_request = db.DateTimeField(db_field="date_request")
    sender = db.ReferenceField(User, required=True, db_field="sender")
    # The receiver is only users, this is the transaction for friends maintenance and governance
    receiver = db.ReferenceField(User, required=True, db_field="receiver")
    transaction_type = db.StringField(db_field="transaction_type", choices = type.keys(), required=True, default="REQ")
    status = db.StringField(db_field="status", choices=status_codes.keys(),default="PND", required = True)
    # Referred Transaction occurs when a Cancel or Unblock transaction occurs.
    # The Cancel refers to (accepted) Request transactions
    # The Unblock refers to Block transactions
    referred_transaction = db.ReferenceField('self', db_field="referred_transaction", required = False)

    def to_obj(self):
        jsonStr=self.to_json()
        retorno=json.loads(jsonStr)
        retorno.pop("_id")
        retorno['sender'] = self.sender.to_obj()
        retorno['receiver'] = self.receiver.to_obj()
        retorno['referred_transaction'] = self.referred_transaction.to_obj()
        retorno["links"]= [
                {"rel": "self", "href": "/transaction/" + self.external_id }
            ]
        return retorno
    
    @staticmethod
    def to_obj_list(trans_list):
        retorno=[trans.to_obj() for trans in trans_list]
        return retorno

    def getStatus(self):
        return self.status_codes[self.status]

    def getTransactionType(self):
        return self.type[self.transaction_type]


class SystemTransaction(db.Document):
    pass