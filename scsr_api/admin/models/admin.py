import json
from uuid import uuid4
from mongoengine import signals
from application import db
from user.models.user import UserDB, UserAO

"""Classes for handling ORM for the administration context.

   Status: Done for the moment.
   TODO: Nothing.

"""

class AdminGroupDB(db.Document):
    """ ORM to reference the groups to be assigned to the admins.
        In system start there are only two basic groups:
           - GOD: Can do whatever he wants
           - common: basically can only list who are users and check scsr freely.
        Future possible groups:
           - gamemanagers: Can approve suggested games
           - genremaintainers: Maps or merges genres
           - systemadmins: Maintains the transactions
           - usersmanagers: Guarantees the sanity of the (social) system by verifying and managing user activities
                - This level allows the manager to invalidate the user classifications.
           - scsrpolice: Guarantees the sanity of the SCSR

        Methods:
            to_obj: Return a dict object representing the class

        Action Methods:
            pre_save: Assigns an external_id if one is missing
    
    """

    external_id=db.StringField(db_field="external_id", required=True)
    group=db.DictField(db_field="group", required=True)

    def to_obj(self):
        """Returns the Object as a Python Dict object
        
            Returns:
                dict -- the instantiated object
        """

        
        jsonStr=self.to_json()
        retorno=json.loads(jsonStr)
        retorno.pop("_id","")
        return retorno

    @classmethod
    def preSave(cls, sender, document, **kwargs):
        """ After saving the genre set the external_id
        
        Arguments:
            sender {UserGameGenre} -- The sender of the signal
            document {UserGameGenre} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())
        pass

signals.pre_save.connect(AdminGroupDB.preSave, sender=AdminGroupDB)


class AdminDB(db.Document):
    """Wraps a user in an admin role
       The admin role differs only from the user in the fact that it is assigned to at least one group (the common).

        Methods:
            to_obj: Return a dict object representing the class

        Action Methods:
            isAdmin(user): Returns true if the user is an admin.
            pre_save: Assigns an external_id if one is missing
    """

    external_id=db.StringField(db_field="external_id", required=True)
    user = db.ReferenceField(UserDB, db_field="user", required=True)
    group = db.ListField(db.ReferenceField(AdminGroupDB), required=True, default=[AdminGroupDB.objects.filter(group__en="common").first])

    def to_obj(self):
        """Returns the Object as a Python Dict object
        
            Returns:
                dict -- the instantiated object ad python dict
        """
        jsonStr=self.to_json()
        retorno=json.loads(jsonStr)
        retorno.pop("_id")
        retorno['user'] = self.user.to_obj()
        return retorno

    def set_admin(self,userao):
        if(not isinstance(userao,UserAO)):
            raise RuntimeError("ERROR: Argument is not a valid UserAO object.")
        if(not hasattr(userao,"external_id")):
            raise RuntimeError("ERROR: User Object is not persisted. It must exists in the base to be assigned.")
        self.user=UserDB.objects.filter(external_id=userao.external_id).first()

    @staticmethod
    def isAdmin(user):
        """Inform if the user is an Admin
        
            Arguments:
                user {UserDB} -- The user ORM object to verify
            
            Returns:
                Boolean -- Returns True if the user is valid and an administrator, false otherwise.
        """

        result=False
        try:
            result=((AdminDB.objects.filter(external_id=user.external_id).first()) or None)
        except:
            # The system can maintain a silent error handling mechanism (as OpenGL) via transactions and messages
            result=False
        return result

    @classmethod
    def preSave(cls, sender, document, **kwargs):
        """ After saving the genre set the external_id
        
        Arguments:
            sender {UserGameGenre} -- The sender of the signal
            document {UserGameGenre} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())
        pass

signals.pre_save.connect(AdminDB.preSave, sender=AdminDB)
