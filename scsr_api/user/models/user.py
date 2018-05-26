from datetime import datetime
import json
from mongoengine import signals
from email.utils import parseaddr
from application import db
from uuid import uuid4
from utils import sanitize



class UserDB(db.Document):
    """
    ORM for the minimal requested data for the User element in the system

    Arguments:
        db {attribute} -- maps to the object attribute of the class.

    Reasons:
        Maintaining the user data in order to guarantee it is not a bot and to provide authentication information.
        The geographic localization can be used for further studies.
    """


    external_id = db.StringField(db_field="external_id") # pylint: disable=no-member
    country = db.StringField(db_field="country") # pylint: disable=no-member
    state = db.StringField(db_field="state") # pylint: disable=no-member
    city = db.StringField(db_field="city") # pylint: disable=no-member
    lang = db.StringField(db_field="lang") # pylint: disable=no-member
    name = db.StringField(db_field="name") # pylint: disable=no-member
    surname = db.StringField(db_field="surname") # pylint: disable=no-member
    username = db.StringField(db_field="username", unique=True) # pylint: disable=no-member
    birthdate = db.DateTimeField(db_field="birthdate", required=True) # pylint: disable=no-member
    email = db.EmailField(db_field="email", unique=True) # pylint: disable=no-member
    password = db.StringField(db_field="password") # pylint: disable=no-member
    avatar = db.StringField(db_field="avatar_url", default="None") # pylint: disable=no-member
    bio = db.StringField(db_field="bio", default="None") # pylint: disable=no-member
    live = db.BooleanField(db_field="live", default = True) # pylint: disable=no-member
    created = db.DateTimeField(db_field="created", default = datetime.utcnow) # pylint: disable=no-member
    updated = db.DateTimeField(db_field="updated", default = datetime.utcnow) # pylint: disable=no-member
    meta = {
        "indexes": [("external_id", "live", "username", "email", "name", "country", "state")]
    }

    def to_obj(self):
        return UserAO.from_db(self)
        """
        return {
            "data":{
                "id": self.external_id,
                "country": self.country,
                "state": self.state,
                "city": self.city,
                "name": self.name,
                "surname": self.surname,
                "username": self.username,
                "email": self.email,
                "password": self.password,
                "created": self.created,
                "avatar": self.avatar,
                "bio": self.bio,
                "live": self.live},
            "links": [
                {"rel": "self", "href": "/users/" + self.external_id }
            ]
        }
        """

    @classmethod
    def preSave(cls, sender, document, **kwargs):
        """ After saving the genre set the external_id
        
        Arguments:
            sender {UserGameGenre} -- The sender of the signal
            document {UserGameGenre} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())

signals.pre_save.connect(UserDB.preSave, sender=UserDB)

class UserAO(object):
    """ Class to represent the data object in the Controller.
    
        Attributes:
            external_id: String
            country: String
            state: String
            city: String
            name: String
            surname: String
            username: String
            email: String
            password: String
            created: datetime
            updated: datetime
            avatar: String
            bio: String
            live: Boolean
            
    """

    def __init__(self):
        self.external_id = None
        self.country = None
        self.state = None
        self.lang=None
        self.city = None
        self.name = None
        self.surname = None
        self.username = None
        self.email = None
        self.password = None
        self.avatar = None
        self.bio = None
        self.birthdate = None
        self.live = None
        self.created = None
        self.updated = None

    def __update_data__(self,db_obj):
        """ Returns a UserAO object from a DB object
        
        Arguments:
            db_obj {UserDB} -- Returns the UserAO object
        """

        self.external_id = db_obj.external_id
        self.country = db_obj.country
        self.lang = db_obj.lang
        self.state = db_obj.state
        self.city = db_obj.city
        self.name = db_obj.name
        self.surname = db_obj.surname
        self.username = db_obj.username
        self.email = db_obj.email
        self.password = db_obj.password
        self.avatar = db_obj.avatar
        self.bio = db_obj.bio
        self.live = db_obj.live
        self.created = db_obj.created
        self.updated = db_obj.updated
        self.birthdate = db_obj.birthdate



    @staticmethod
    def from_db(db_obj):
        """ Returns a UserAO object from a DB object
        
        Arguments:
            db_obj {UserDB} -- Returns the UserAO object
        """

        retorno=UserAO()
        retorno.external_id = db_obj.external_id
        retorno.country = db_obj.country
        retorno.lang = db_obj.lang
        retorno.state = db_obj.state
        retorno.city = db_obj.city
        retorno.name = db_obj.name
        retorno.surname = db_obj.surname
        retorno.username = db_obj.username
        retorno.email = db_obj.email
        retorno.password = db_obj.password
        retorno.avatar = db_obj.avatar
        retorno.bio = db_obj.bio
        retorno.live = db_obj.live
        retorno.created = db_obj.created
        retorno.updated = db_obj.updated
        retorno.birthdate = db_obj.birthdate
        return retorno

    def to_json(self):
        retorno={
            "external_id" :getattr(self,"external_id",None),
            "country" :getattr(self,"country",None),
            "state" :getattr(self,"state",None),
            "lang" :getattr(self,"lang",None),
            "city" :getattr(self,"city",None),
            "name" :getattr(self,"name",None),
            "surname" :getattr(self,"surname",None),
            "username" :getattr(self,"username",None),
            "email" :getattr(self,"email",None),
            "password" :getattr(self,"password",None),
            "avatar" :getattr(self,"avatar",None),
            "bio" :getattr(self,"bio",None),
            "live" :getattr(self,"live",None),
            "created" :getattr(self,"created",None),
            "updated" :getattr(self,"updated",None),
            "birthdate" :getattr(self,"birthdate",None)
        }
        return retorno

    def set_country(self, dado):
        valid, self.country=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("country")
        return True

    def set_lang(self, dado):
        valid, self.lang=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("lang")
        return True

    def set_state(self, dado):
        valid, self.state=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("state")
        return True

    def set_city(self, dado):
        valid, self.city=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("city")
        return True

    def set_name(self, dado):
        valid, self.name=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("name")
        return True

    def set_surname(self, dado):
        valid, self.surname=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("surname")
        return True

    def set_username(self, dado):
        valid, self.username=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("username")
        return True

    def set_email(self, dado):
        valid, self.email=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("email")
        return True

    def set_password(self, dado):
        valid, self.password=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("password")
        return True

    def set_avatar(self, dado):
        valid, self.avatar=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("avatar")
        return True

    def set_bio(self, dado):
        valid, self.bio=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("bio")
        return True

    def set_birthdate(self, dado):
        valid, self.birthdate=sanitize.sanitize_db(dado)
        if(not valid):
            return False
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("birthdate")
        return True


    def wasModified(self):
        return hasattr(self,"modified")

    def save(self):
        to_save=None
        #does it have external_id?
        if(self.external_id):
            #retrieve (or create) the DB object
            to_save=UserDB.objects.filter(external_id=self.external_id).first() # pylint: disable=no-member
            if(not to_save):
                raise RuntimeError("ERROR: Unmatched Object to Update. User not found in DB. External_ID: "+self.external_id)
                return #do not continue
            if(not self.wasModified()):
                return
            else:
                #future development for historical data
                to_save.updated=datetime.utcnow()
                pass
        else:
            to_save=UserDB()
        #external_id None or already set in the search above.
        # TODO: SANITIZE DATA!
        to_save.country = self.country
        to_save.state = self.state
        to_save.city = self.city
        to_save.name = self.name
        to_save.surname = self.surname
        to_save.username = self.username
        to_save.email = self.email
        to_save.password = self.password
        to_save.avatar = self.avatar
        to_save.bio = self.bio
        to_save.birthdate = self.birthdate
        to_save.live = True
        if(hasattr(self,"modified")):
            self.__delattr__("modified")
        to_save.save()
        self.__update_data__(to_save)

    @staticmethod
    def get_schema():
        """
        The Schema to validate the user data.
        """
        schema = {
                "type": "object",
                "properties": {
                    "country" : {"type": "string", "pattern": "^[A-Z]{2}$"},
                    "state" : {"type": "string", "pattern": "^[A-Z]{2}$"},
                    "city" : {"type": "string"},
                    "lang": {"type": "string"},
                    "name" : {"type": "string"},
                    "surname" : {"type": "string"},
                    "username" : {"type": "string"},
                    "email" : {"type": "string", "pattern":"[^@]+@[^@]+\.[^@]+"},
                    "avatar": {"type": "string"},
                    "password" : {"type": "string"},
                    "bio": {"type": "string"},
                    "live" : {"type":"boolean"},
                    "created": {"type":"datetime"},
                    "updated": {"type":"datetime"},
                    "birthdate": {"type":"datetime"}
                },
                "required": ['country', 'state', 'lang', 'name', 'surname', 'username', 'email', 'password', 'birthdate']
            }
        return schema

    @staticmethod
    def get_user_username(uname):
        retorno_temp=UserDB.objects.filter(username=uname).first() # pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=retorno_temp.to_obj()
        return retorno

    @staticmethod
    def get_user_email(uname):
        retorno_temp=UserDB.objects.filter(email=uname).first() # pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=retorno_temp.to_obj()
        return retorno

    @staticmethod
    def get_users_city(cityname):
        retorno_temp=UserDB.objects.filter(city=cityname) # pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=[user.to_obj() for user in retorno_temp]
        return retorno

    @staticmethod
    def get_users_state(statename):
        retorno_temp=UserDB.objects.filter(state=statename) # pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=[user.to_obj() for user in retorno_temp]
        return retorno

    @staticmethod
    def get_users_country(countryname):
        retorno_temp=UserDB.objects.filter(country=countryname) # pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=[user.to_obj() for user in retorno_temp]
        return retorno

    @staticmethod
    def get_users_surname(name):
        retorno_temp=UserDB.objects(__raw__={"surname":{'$regex':name,'$options':'i'}})# pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=[user.to_obj() for user in retorno_temp]
        return retorno
    
    @staticmethod
    def get_users_name(name):
        retorno_temp=UserDB.objects(__raw__={"name":{'$regex':name,'$options':'i'}})# pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=[user.to_obj() for user in retorno_temp]
        return retorno
    
