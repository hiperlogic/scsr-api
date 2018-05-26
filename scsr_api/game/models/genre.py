from mongoengine import signals
from application import db
from uuid import uuid4
import json
from datetime import datetime

from utils import sanitize
from sys_app.models.localization import TranslationsAO


class GenreDB(db.Document):
    """ Genre will store the genres to be assigned to games. Represents the Genre object to be mapped to the database



        Attributes:
            external_id - unique representation data to send to clients
            genre - 
    
    
        Attributes: 
            external_id {String} -- to pass to the client (string)
            genre {dict} -- a key-value data set indicating the idiom and the value representing the genre in the idiom.
                Example: {'en':'adventure'}
            active {boolean} -- informs if the genre is active (valid)
            assigned_to {GenreDB} -- when reassigned, the current genre is no longer valid, this value is the one to be used
            assigned_from {list of GenreDB} -- One genre may be assigned from some others. Having this data does not validate the genre as active. It is possible to reassign it to other genre.


        Methods:
            to_obj: Returns a python dict representation of the data

        Action Methods:
            increase_genre: Increases a genre count (or initializes one with 1) in the game representation
            decrease_genre: Decreases a genre count (maintaining the lower limit as 0) in the game representation
            get_genres: Returns a list of the ORM objects of all the genres in game whose count>0
            update_data: Disregards thecurrent genreCount and generates another one from the UserGameGenre collection

        Class/Static Methods:
            map_genre
            get_all_genres
            get_genres (in language)
            get_genre_obj
            get_or_create_genre

    """

    external_id = db.StringField(db_field="external_id", unique=True) # pylint: disable=no-member
    genre = db.DictField(db_field = "genre") # pylint: disable=no-member
    reassigned_to=db.ReferenceField("self",db_field='reassiged_to') # pylint: disable=no-member
    reassigned_from=db.ListField(db.ReferenceField('self'),db_field='reassiged_from') # pylint: disable=no-member
    created = db.DateTimeField(db_field="created", default = datetime.utcnow) # pylint: disable=no-member
    updated = db.DateTimeField(db_field="updated", default = datetime.utcnow) # pylint: disable=no-member
    active = db.BooleanField(db_field="active", required=True, default=True) # pylint: disable=no-member

    meta = {
        "indexes": [("external_id", "genre", "active")]
    }


    def to_obj(self):
        return GenreAO.from_db(self)

    def get_reassigned_to_obj(self):
        retorno=None
        if(self.reassigned_to):
            retorno=self.reassigned_to.to_obj()
        return retorno

    @staticmethod
    def get_genre(eid):
        if not isinstance(eid,str):
            raise TypeError("ERROR: Invalid type for the identification data.")
        dbdata = GenreDB.objects.filter(external_id=eid).first() # pylint: disable=no-member
        if (not dbdata) or (not dbdata.external_id==eid):
            raise RuntimeError("ERROR: Persistent Data not Found or Mismatched.")
        return dbdata


    @staticmethod #TODO:
    def reassign(old,new):
        """
            Maps the old genre, making it inactive to the new genre, calling the update in the games that were classified with both via UserGameGenre.
            The process is done via UserGameGenre due to the possibility of some users to have assigned both genres to a game.
            This invalidates one of the genres and maintains the sanity of the statistical data within the game.
            This reassignment has 2 purposes:
                1 - replace one genre for the other or
                2 - merge 2 genres representing the same, but with different languages.
                For the 1st, imagine someone set "graphic adventure" for a genre and other set just "adventure". Both represents the adventure genre, but one specifically states it has graphics
                It is of no concern of ours if the game has graphics or not, only the genre, so, the 1st genre will be disregarded.

                For the 2nd, imagine one started a genre for 'pt' saying: "aventura", and other set a genre for 'en' saying: "adventure". Both represent the same genre, but in different language
                This form, the assignment is a merge, producing 1 genre with the 2 idioms in the list.
        Arguments:
            old {GenreDB} -- The genre to become inactive
            new {GenreDB} -- The genre to become active

             TODO: This is a purely administrative task. The genres will be requested to be add by the users, the administrators will attend.
                    So, if no user will tamper with this data, it can be coded later.
        """
        #retrieve all users who assigned only the old genre to the game
        # onlyOld=UserGameGenre.objects(__raw__={"$and":{"$not":{"$in":new},"$in":old}})
        # for ugg in onlyOld:
        #   ugg.addGenre(new)
        #   ugg.removeGenre(old)
        #   ugg.save()
        ### remove the old genre, add the new
        #retrieve all users who assigned both genres to the game
        # both=UserGameGenre.objects(__raw__={"$and":{$in":new,"$in":old})
        # for ugg in both:
        #   ugg.remove(old)
        #   ugg.save()
        ### remove just the old genre
        #assign the references
        # old.reassigned_to=new
        # old.active=false
        # if not new.reassigned_from:
        #    new.reassigned_from=[]
        # new.reassigned_from.append(old)
        # old.save()
        # new.save()
        pass


    @classmethod
    def pre_save(cls, sender, document, **kwargs):
        """ prior to saving the genre set the external_id
        
        Arguments:
            sender {GenreDB} -- The sender of the signal
            document {GenreDB} -- The instance of the document
        """
        if(not document.external_id):
            document.external_id=str(uuid4())

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        """ After saving the genre check if the GamesGenresDB data was created
        
        Arguments:
            sender {GenreDB} -- The sender of the signal
            document {GenreDB} -- The instance of the document
        """
        from game.models.user_game_genre import GamesGenresDB
        genreGameList=GamesGenresDB.objects.filter(genre=document).first() # pylint: disable=no-member
        if(not genreGameList):
            #there is no genre for the games to be assigned to... create one
            genreGameList=GamesGenresDB()
            genreGameList.genre=document
            genreGameList.gamesList=[]
            genreGameList.save()

signals.pre_save.connect(GenreDB.pre_save, sender=GenreDB)
signals.post_save.connect(GenreDB.post_save, sender=GenreDB)


class GenreAO(object):
    def __init__(self):
        self.external_id = None
        self.genre = {}
        self.reassigned_to = None
        self.reassigned_from = []
        self.active = None
        self.created=None
        self.updated=None


    def __update_data__(self, data):
        self.external_id = data.external_id
        self.genre = data.genre
        self.active = data.active
        self.created = data.created
        self.updated = data.updated
        #reassigned to and reassigned from are not manipulated via GenreAO.
        self.reassigned_to = data.get_reassigned_to_obj()
        self.reassigned_from = [obj.to_obj() for obj in data.reassigned_from]


    @staticmethod
    def from_db(db_obj):
        retorno=GenreAO()
        retorno.external_id = db_obj.external_id
        retorno.genre = db_obj.genre
        retorno.active = db_obj.active
        retorno.created = db_obj.created
        retorno.updated = db_obj.updated
        #reassigned to and reassigned from are not manipulated via GenreAO.
        retorno.reassigned_to = db_obj.reassigned_to.to_obj()
        retorno.reassigned_from = [obj.to_obj() for obj in db_obj.reassigned_from]
        #
        return retorno

    @staticmethod
    def get_missing_translations():
        """ Returns the missing active genres translation in the system
        
        Returns:
            dict -- A dict of the form {lang:[missing]} with a list of missing genre application objects for the language
        """

        langs=[lang.code for lang in TranslationsAO.get_system_languages()]
        missing={}
        for lang in langs:
            missing[lang]=[gen.to_obj() for gen in GenreDB.objects(__raw__={"genre."+lang:{"$exists":False}, "active":True})]  # pylint: disable=no-member
        return missing

    def wasModified(self):
        return hasattr(self,"modified")

    def save(self):
        to_save=None
        if(self.external_id):
            to_save=GenreDB.objects.filter(external_id=self.external_id).first() # pylint: disable=no-member
            if(not to_save):
                raise RuntimeError("ERROR: Unmatched object to update. Genre not found in DB. External_ID: "+self.external_id)
            if(not self.wasModified()):
                return
            else:
                to_save.updated = datetime.utcnow()
        else:
            to_save=GenreDB()
        self.__delattr__("modified")
        #The genre can only be modified via setGenre
        to_save.genre = self.genre
        to_save.active = self.active
        to_save.save()
        self.__update_data__(to_save)

    def set_genre(self,lang,data):
        valid_lang, vlang=sanitize.sanitize_db(lang)
        valid_data, vdata=sanitize.sanitize_db(data)
        if(not valid_lang):
            raise RuntimeError("ERROR: Language not supported or malicious: "+vlang)
        if(not valid_data):
            raise RuntimeError("ERROR: Data not supported or malicious: "+vdata)
        if(not TranslationsAO.has_language(vlang)):
            #if the system does not support the lang
            raise RuntimeError("ERROR: Language not supported: "+vlang)
        self.genre[vlang]=vdata
        if(not hasattr(self,"modified")):
            self.modified=set()
        self.modified.add("genre")
        return True

    def to_json(self):
        retorno={
        "external_id" : getattr(self,"external_id",None),
        "genre" : getattr(self,"genre",None),
        "reassigned_to" : getattr(self,"reassigned_to",None),
        "reassigned_from" : [obj.to_json() for obj in self.reassigned_from],
        "active" : getattr(self,"active",None),
        "created" : getattr(self,"created",None),
        "updated" : getattr(self,"updated",None),
        }
        return retorno

    @staticmethod
    def get_all_genres():
        """Provides all the genre objects in the system.
        """
        return [genre.to_obj() for genre in GenreDB.objects()] # pylint: disable=no-member

    @staticmethod
    def get_genres(lang):
        """ Provides a list of string of the genres in the specified language
        
        Arguments:
            lang {String} -- The idiom to retrieve the genres
        """
        dados = GenreDB.objects() # pylint: disable=no-member
        retorno = [dado.genre[lang] for dado in dados]
        return retorno

    @staticmethod
    def get_genre(lang,genre):
        """ Provides an object mapped instance for the desired genre in the desired lang or None
        
        Arguments:
            lang {String} -- The language to seek the genre ex: 'pt'
            genre {String} -- The genre name ex: 'aventura'
        """
        retorno_temp = GenreDB.objects( __raw__ = {"genre."+lang.lower():genre, "active":True}).first() # pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=retorno_temp.to_obj()
        return retorno

    @staticmethod
    def suggest_genre(lang,genre):
        retorno_temp = GenreDB.objects( __raw__ = {"genre."+lang.lower():{'$regex':genre,'$options':'i'}, "active":True}) # pylint: disable=no-member
        retorno=None
        if(retorno_temp):
            retorno=[genre.to_obj() for genre in retorno_temp]
        return retorno

    def __get_persisted__(self):
        if not self.external_id:
            return None
        return GenreDB.objects.filter(external_id=self.external_id).first() # pylint: disable=no-member