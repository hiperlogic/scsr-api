from user.templates import user_obj, users_obj

def transaction_obj(transaction):
    return{
        "type": transaction.type,
        "status": transaction.status,
        "receiver": user_obj(transaction.receiver),
        "sender": user_obj(transaction.sender),
        "date_request": transaction.dateRequest,
        "links": [
            {"rel": "self", "href": "/social/transaction" + transaction.receiver.external_id }
        ]
    }

def transactions_obj(tran_list):
    results = []
    for transaction in tran_list.items:
        results.append(transaction_obj(transaction))
    return results

def social_obj(social):
    return {
        "user": user_obj(social.user),
        "friends": users_obj(social.friends),
        "friends_pending": transactions_obj(social.friendsPending),
        "friends_request": transactions_obj(social.friendsRequest),
        "links": [
            {"rel": "self", "href": "/social/" + social.user.external_id }
        ]
    }